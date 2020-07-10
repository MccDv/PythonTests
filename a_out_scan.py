from __future__ import absolute_import, division, print_function

import math
import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
from mcculw.enums import BoardInfo, InfoType, ULRange
import util
from props.ao import AnalogOutputProps
from mcculw.ul import ULError
from time import sleep

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

    ao_props = AnalogOutputProps(board_num)
    if ao_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    index = 0
    for ao_range in ao_props.available_ranges:
        print(str(index) + ": ", ao_range, sep = " ")
        index += 1
    range_index = int(input('\nSelect range (default 0): ') or '0')
    util.clear_screen()
    ai_range = ao_props.available_ranges[range_index]
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")

    rate = int(input('\nSelect rate (default 100): ') or '100')
    points_per_channel = int(input('Select points per channel (default 1000): ') or '1000')
    low_chan =  int(input('Select first channel (default 0): ') or '0')
    def_high_chan = min(3, ao_props.num_chans - 1)
    def_high = str(def_high_chan)
    high_chan = int(input('Select last channel (default ' +
                          def_high + '): ') or def_high)
    num_chans = high_chan - low_chan + 1

    #rate = 100
    #points_per_channel = 1000
    total_count = points_per_channel * num_chans

    ao_range = ao_props.available_ranges[0]

    # Allocate a buffer for the scan
    memhandle = ul.win_buf_alloc(total_count)
    # Convert the memhandle to a ctypes array
    # Note: the ctypes array will no longer be valid after win_buf_free
    # is called.
    # A copy of the buffer can be created using win_buf_to_array
    # before the memory is freed. The copy can be used at any time.
    ctypes_array = util.memhandle_as_ctypes_array(memhandle)

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    frequencies = add_example_data(
        board_num, ctypes_array, ao_range, num_chans, rate,
        points_per_channel)

    print()
    for ch_num in range(low_chan, high_chan + 1):
        print(
            "\tChannel " + str(ch_num) + " Output Signal Frequency: "
            + str(frequencies[ch_num - low_chan]))

    try:
        # Start the scan
        ul.a_out_scan(
            board_num, low_chan, high_chan, total_count, rate, ao_range,
            memhandle, ScanOptions.BACKGROUND)

        # Wait for the scan to complete
        print("\nWaiting for output scan to complete...", end="")
        status = Status.RUNNING
        index = 1
        while status != Status.IDLE:

            # Slow down the status check so as not to flood the CPU
            time.sleep(0.5)

            status, curr_count, curr_index = ul.get_status(
                board_num, FunctionType.AOFUNCTION)
            s = str(status.name)
            i = str(curr_index)
            c = str(curr_count)
            util.print_at(12, 4, 'Status: ' + s + '\t\tCount: ' + c + '\t\tIndex: ' + i)
            util.print_at(14, index, ".")
            index += 1
        util.clear_line(14, 1)
        print("")

        print("\nScan completed successfully.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


def add_example_data(board_num, data_array, ao_range, num_chans, rate,
                     points_per_channel):
    # Calculate frequencies that will work well with the size of the array
    frequencies = []
    for channel_num in range(num_chans):
        frequencies.append(
            (channel_num + 1) / (points_per_channel / rate) * 10)

    # Calculate an amplitude and y-offset for the signal
    # to fill the analog output range
    amplitude = (ao_range.range_max - ao_range.range_min) / 2
    y_offset = (amplitude + ao_range.range_min) / 2

    # Fill the array with sine wave data at the calculated frequencies.
    # Note that since we are using the SCALEDATA option, the values
    # added to data_array are the actual voltage values that the device
    # will output
    data_index = 0
    for point_num in range(points_per_channel):
        for channel_num in range(num_chans):
            freq = frequencies[channel_num]
            value = amplitude * math.sin(
                2 * math.pi * freq * point_num / rate) + y_offset
            raw_value = ul.from_eng_units(
                board_num, ao_range, value)
            data_array[data_index] = raw_value
            data_index += 1

    return frequencies


if __name__ == '__main__':
    run_example()
