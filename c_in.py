from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import CounterChannelType, BoardInfo, InfoType
from console import util
from props.counter import CounterProps
from mcculw.ul import ULError
from time import sleep

use_device_detection = True


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

    ctr_props = CounterProps(board_num)
    if ctr_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    separator = ''
    print('\nCounter numbers: ', end = '')
    for channel in ctr_props.counter_info:
        if (channel.type == CounterChannelType.CTREVENT) \
           or (channel.type == CounterChannelType.CTRSCAN):
                print(separator + str(channel.channel_num), end = '')
                separator = ', '
    counter_num = int(input('\n\nChannel selected (default 0): ') or '0')
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")

    loop_count = int(input('\nEnter loop count (default 50): ') or '50')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    try:
        ul.c_clear(board_num, counter_num)
        for x in range(0, loop_count):
            # Get a value from the device
            value = ul.c_in_32(board_num, counter_num)
            # Display the value
            util.print_at(2, 2, "Counter " +
                          str(counter_num) + " value: " + str(value))
            print()
            sleep(0.2)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
