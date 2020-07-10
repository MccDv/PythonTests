from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions
from mcculw.enums import BoardInfo, InfoType, ULRange
import util
from props.ai import AnalogInputProps
from mcculw.ul import ULError

def run_example():

    util.clear_screen()
    board_num = 0
    use_device_detection = True
    response = input('\nUse Instacal? (default n): ') or 'n'
    if response == 'y':
        use_device_detection = False

    util.clear_screen()
    if use_device_detection:
        ul.ignore_instacal()
        devices = util.detect_devices()
        if len(devices) == 0:
            print("Could not find device.")
            return
        try:
            board_num = int(input('\nEnter device number (default 0): ') or '0')
            # Add the device to the UL.
            device = devices[board_num]
            ul.create_daq_device(board_num, device)
            prod_name = device.product_name
            prod_id = device.unique_id
        except ULError as e:
            util.print_ul_error(e)
            return
    else:
        try:
            board_list = util.get_installed_boards()
            def_board = str(board_list[0])
            print('Board numbers of boards installed with Instacal: ' +
                  str(board_list))
            board_num = int(input('\nEnter device number (default ' +
                                  def_board + '): ') or def_board)
            prod_name = ul.get_board_name(board_num)
            info_type = InfoType.BOARDINFO
            config_item = BoardInfo.DEVUNIQUEID
            max_config_len = 32
            prod_id = ul.get_config_string(info_type, board_num, 0, config_item, max_config_len)
        except ULError as e:
            util.print_ul_error(e)
            return
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    print()

    ai_props = AnalogInputProps(board_num)
    if ai_props.num_ai_chans < 1:
        util.print_unsupported_example(board_num)
        return

    index = 0
    for ai_range in ai_props.available_ranges:
        print(str(index) + ": ", ai_range, sep = " ")
        index += 1
    range_index = int(input('\nSelect range (default 0): ') or '0')
    util.clear_screen()
    ai_range = ai_props.available_ranges[range_index]
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    print()
    
    rate = int(input('\nSelect rate (default 100): ') or '100')
    points_per_channel = int(input('Select points per channel (default 10): ') or '10')
    low_chan =  int(input('Select first channel (default 0): ') or '0')
    def_high_chan = min(3, ai_props.num_ai_chans - 1)
    def_high = str(def_high_chan)
    high_chan = int(input('Select last channel (default ' +
                          def_high + '): ') or def_high)
    num_chans = high_chan - low_chan + 1
    high_chan = min(3, ai_props.num_ai_chans - 1)
    num_chans = high_chan - low_chan + 1

    total_count = points_per_channel * num_chans

    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    print()

    scan_options = ScanOptions.FOREGROUND

    if ScanOptions.SCALEDATA in ai_props.supported_scan_options:
        # If the hardware supports the SCALEDATA option, it is easiest to
        # use it.
        scan_options |= ScanOptions.SCALEDATA

        memhandle = ul.scaled_win_buf_alloc(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array_scaled method for scaled
        # buffers.
        ctypes_array = util.memhandle_as_ctypes_array_scaled(memhandle)
    elif ai_props.resolution <= 16:
        # Use the win_buf_alloc method for devices with a resolution <= 16
        memhandle = ul.win_buf_alloc(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array method for devices with a
        # resolution <= 16.
        ctypes_array = util.memhandle_as_ctypes_array(memhandle)
    else:
        # Use the win_buf_alloc_32 method for devices with a resolution > 16
        memhandle = ul.win_buf_alloc_32(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array_32 method for devices with a
        # resolution > 16
        ctypes_array = util.memhandle_as_ctypes_array_32(memhandle)

    # Note: the ctypes array will no longer be valid after win_buf_free is
    # called.
    # A copy of the buffer can be created using win_buf_to_array or
    # win_buf_to_array_32 before the memory is freed. The copy can be used
    # at any time.

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    try:
        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, total_count,
            rate, ai_range, memhandle, scan_options)

        print("Scan completed successfully. Data:\n")

        # Create a format string that aligns the data in columns
        row_format = "{:>5}" + "{:>10}" * num_chans

        # Print the channel name headers
        labels = []
        labels.append("Index")
        for ch_num in range(low_chan, high_chan + 1):
            labels.append("CH" + str(ch_num))
        print(row_format.format(*labels))

        # Print the data
        data_index = 0
        for index in range(points_per_channel):
            display_data = [index]
            for _ in range(num_chans):
                if ScanOptions.SCALEDATA in scan_options:
                    # If the SCALEDATA ScanOption was used, the values
                    # in the array are already in engineering units.
                    eng_value = ctypes_array[data_index]
                else:
                    # If the SCALEDATA ScanOption was NOT used, the
                    # values in the array must be converted to
                    # engineering units using ul.to_eng_units().
                    eng_value = ul.to_eng_units(
                        board_num, ai_range, ctypes_array[data_index])
                data_index += 1
                display_data.append('{:.3f}'.format(eng_value))
            # Print this row
            print(row_format.format(*display_data))
    except ULError as e:
        util.print_ul_error(e)
    finally:
        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        ul.win_buf_free(memhandle)

        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
