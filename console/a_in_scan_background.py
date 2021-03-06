from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from time import sleep
from ctypes import cast, POINTER, c_double, c_ushort, c_ulong

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device


def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed.
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    board_num = 0
    rate = 100
    points_per_channel = 1000
    memhandle = None

    try:
        if use_device_detection:
            #type_list = [120, 310, 197, 311]
            type_list = [197]
            config_first_detected_device(board_num, type_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ai_info = daq_dev_info.get_ai_info()

        low_chan = 0
        high_chan = min(3, ai_info.num_chans - 1)
        num_chans = high_chan - low_chan + 1

        total_count = points_per_channel * num_chans

        ai_range = ai_info.supported_ranges[0]

        scan_options = ScanOptions.BACKGROUND

        if ScanOptions.SCALEDATA in ai_info.supported_scan_options:
            # If the hardware supports the SCALEDATA option, it is easiest to
            # use it.
            scan_options |= ScanOptions.SCALEDATA

            memhandle = ul.scaled_win_buf_alloc(total_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_double))
        elif ai_info.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <= 16
            memhandle = ul.win_buf_alloc(total_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ushort))
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution > 16
            memhandle = ul.win_buf_alloc_32(total_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ulong))

        # Note: the ctypes array will no longer be valid after win_buf_free is
        # called.
        # A copy of the buffer can be created using win_buf_to_array or
        # win_buf_to_array_32 before the memory is freed. The copy can be used
        # at any time.

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Error: Failed to allocate memory')

        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, total_count,
            rate, ai_range, memhandle, scan_options)

        # Create a format string that aligns the data in columns
        row_format = '{:>12}' * num_chans

        # Print the channel name headers
        labels = []
        for ch_num in range(low_chan, high_chan + 1):
            labels.append('CH' + str(ch_num))
        print(row_format.format(*labels))

        # Start updating the displayed values
        status, curr_count, curr_index = ul.get_status(
            board_num, FunctionType.AIFUNCTION)
        while status != Status.IDLE:
            # Make sure a data point is available for display.
            if curr_count > 0:
                # curr_index points to the start of the last completed
                # channel scan that was transferred between the board and
                # the data buffer. Display the latest value for each
                # channel.
                display_data = []
                for data_index in range(curr_index, curr_index + num_chans):
                    if ScanOptions.SCALEDATA in scan_options:
                        # If the SCALEDATA ScanOption was used, the values
                        # in the array are already in engineering units.
                        eng_value = ctypes_array[data_index]
                    else:
                        # If the SCALEDATA ScanOption was NOT used, the
                        # values in the array must be converted to
                        # engineering units using ul.to_eng_units().
                        eng_value = ul.to_eng_units(board_num, ai_range,
                                                    ctypes_array[data_index])
                    display_data.append('{:.3f}'.format(eng_value))
                print(row_format.format(*display_data))

            # Wait a while before adding more values to the display.
            sleep(0.5)

            status, curr_count, curr_index = ul.get_status(
                board_num, FunctionType.AIFUNCTION)

        # Stop the background operation (this is required even if the
        # scan completes successfully)
        ul.stop_background(board_num, FunctionType.AIFUNCTION)

        print('Scan completed successfully')
    except Exception as e:
        print('\n', e)
    finally:
        if memhandle:
            # Free the buffer in a finally block to prevent a memory leak.
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
