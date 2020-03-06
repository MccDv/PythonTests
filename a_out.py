from __future__ import absolute_import, division, print_function

import math
import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import FunctionType, Status, BoardInfo, InfoType, ULRange
from console import util
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
    
    ao_props = AnalogOutputProps(board_num)
    if ao_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    separator = '\t'
    chan = 0
    print("\nChannels\n")
    for channel in range(0, ao_props.num_chans):
        print(separator + str(channel), end = '')
        separator = ', '
    chan = int(input('\n\nChannel selected (default 0): ') or '0')
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")
    print()

    #check for configured range per channel
    info_type = InfoType.BOARDINFO
    config_item = BoardInfo.DACRANGE
    hard_range = ul.get_config(info_type, board_num, chan, config_item)
    if hard_range not in ao_props.available_ranges:
        print("0: ", ULRange(hard_range).name)
    else:
        index = 0
        for ao_range in ao_props.available_ranges:
            print(str(index) + ": ", ao_range, sep = " ")
            index += 1

    range_index = int(input('\nSelect range (default 0): ') or '0')
    util.clear_screen()
    ao_range = ao_props.available_ranges[range_index]
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")

    loop_count = int(input('\nEnter loop count (default 50): ') or '50')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    index = 0
    data_value = 2**ao_props.resolution - 1
    try:
        for x in range(0, loop_count):
            # Write output value
            out_data = (index % 2) * data_value
            ul.a_out(board_num, chan, ao_range, out_data)
            util.clear_line(2, 2)
            util.print_at(2, 2, "Output " + str(out_data))
            index += 1
            sleep(0.2)
        print()
    except ULError as e:
        util.print_ul_error(e)
    finally:
        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
