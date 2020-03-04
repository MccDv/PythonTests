from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import TempScale
from mcculw.ul import ULError
from time import sleep

from console import util
from props.ai import AnalogInputProps
import sys

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

    ai_props = AnalogInputProps(board_num)
    if ai_props.num_ti_chans < 1:
        util.print_unsupported_example(board_num)
        return
    print('\nChannels: 0', end = '')
    for ti_chan in range(1, ai_props.num_ti_chans):
        print(', ' + str(ti_chan), end = '')
    channel = int(input('\n\nChannel selected: '))
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          device.product_name + " (" + device.unique_id + ")")

    try:
        for x in range(0, 50):
            # Get the value from the device (optional parameters omitted)
            value = ul.t_in(board_num, channel, TempScale.CELSIUS)

            # Display the value
            util.print_at(2, 2, "Channel " + str(channel) + " value (deg C): " + str(value))
            sleep(0.5)
        print()
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
