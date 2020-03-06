from __future__ import absolute_import, division, print_function

import time
from time import sleep

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import BoardInfo, InfoType, CounterChannelType
from console import util
from props.counter import CounterProps
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

    ctr_props = CounterProps(board_num)

    # Find a timer channel on the board
    first_chan = next(
        (channel for channel in ctr_props.counter_info
         if channel.type == CounterChannelType.CTRTMR), None)

    if first_chan == None:
        util.print_unsupported_example(board_num)
        return

    separator = ''
    print('\nTimer numbers: ', end = '')
    for channel in ctr_props.counter_info:
        if (channel.type == CounterChannelType.CTRPULSE):
            print(separator + str(channel.channel_num), end = '')
            separator = ', '
    timer_num = int(input('\n\nTimer selected (default 0): ') or '0')
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
         prod_name + " (" + prod_id+ ")")
    frequency = 100

    loop_count = 2 * int(input('\nEnter seconds to output pulses (default 5): ') or '5')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
         prod_name + " (" + prod_id+ ")")
    try:
        # Start the timer output
        actual_frequency = ul.timer_out_start(
            board_num, timer_num, frequency)

        # Print information about the output
        print(
            "\nOutputting " + str(actual_frequency) + " Hz to timer channel "
            + str(timer_num) + ".")

        # Wait for specified seconds
        for x in range(0, loop_count):
            print('.', sep = ' ', end = '', flush=True)
            time.sleep(0.5)

        # Stop the timer output
        ul.timer_out_stop(board_num, timer_num)

        print("\n\nTimer output stopped.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
