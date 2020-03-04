from __future__ import absolute_import, division, print_function

import time
from time import sleep
import sys

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.ul import ULError

from console import util
from props.counter import CounterProps


use_device_detection = True


def run_example():
    board_num = 0

    util.clear_screen()
    if use_device_detection:
        ul.ignore_instacal()
        devices = util.detect_devices()
        if len(devices) == 0:
            print("Could not find device.")
            return
        try:
            board_num = int(input('\nEnter device number: '))
            # Add the device to the UL.
            device = devices[board_num]
            ul.create_daq_device(board_num, device)
            util.clear_screen()
            print("Device " + str(board_num) + " selected: " +
                  device.product_name + " (" + device.unique_id + ")")
        except ULError as e:
            util.print_ul_error(e)
            return

    ctr_props = CounterProps(board_num)

    # Find a pulse timer channel on the board
    first_chan = next(
        (channel for channel in ctr_props.counter_info
         if channel.type == CounterChannelType.CTRPULSE), None)

    if first_chan == None:
        util.print_unsupported_example(board_num)
        return

    separator = ''
    print('\nTimer numbers: ', end = '')
    for channel in ctr_props.counter_info:
        if (channel.type == CounterChannelType.CTRPULSE):
            print(separator + str(channel.channel_num), end = '')
            separator = ', '
    timer_num = int(input('\n\nTimer selected: '))
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          device.product_name + " (" + device.unique_id + ")")
    #timer_num = first_chan.channel_num
    frequency = 100
    duty_cycle = 0.5

    try:
        # Start the pulse timer output (optional parameters omitted)
        actual_frequency, actual_duty_cycle, _ = ul.pulse_out_start(
            board_num, timer_num, frequency, duty_cycle)

        # Print information about the output
        print(
            "\nOutputting " + str(actual_frequency)
            + " Hz with a duty cycle of " + str(actual_duty_cycle)
            + " to pulse timer channel " + str(timer_num) + ".")

        # Wait for 5 seconds
        for x in range(0, 10):
            print('.', sep = ' ', end = '', file=sys.stdout, flush=True)
            time.sleep(0.5)

        # Stop the pulse timer output
        ul.pulse_out_stop(board_num, timer_num)

        print("\n\nTimer output stopped.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
