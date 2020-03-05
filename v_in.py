from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.ul import ULError

from console import util
from props.ai import AnalogInputProps
from time import sleep

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
            board_num = int(input('\nEnter device number (default 0): ') or '0')
            # Add the device to the UL.
            device = devices[board_num]
            ul.create_daq_device(board_num, device)
            util.clear_screen()
            print("Device " + str(board_num) + " selected: " +
                  device.product_name + " (" + device.unique_id + ")")
        except ULError as e:
            util.print_ul_error(e)
            return

    channel = 0

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
          device.product_name + " (" + device.unique_id + ")")

    loop_count = int(input('\nEnter loop count (default 50): ') or '50')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          device.product_name + " (" + device.unique_id + ")")
    try:
        for x in range(0, loop_count):
            # Get a value from the device
            if ai_props.resolution <= 16:
                # Use the v_in method for devices with a resolution <= 16
                # (optional parameter omitted)
                value = ul.v_in(board_num, channel, ai_range)
            else:
                # Use the v_in_32 method for devices with a resolution > 16
                # (optional parameter omitted)
                value = ul.v_in_32(board_num, channel, ai_range)

            # Display the value
            util.clear_line(2, 2)
            util.print_at(2, 2, "Value: \t" + str(value) + "\n")
            print()
            sleep(0.2)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
