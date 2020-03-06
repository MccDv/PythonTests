from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import BoardInfo, InfoType, ULRange
from mcculw.ul import ULError
from time import sleep

from console import util
from props.ai import AnalogInputProps

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
            print('Board numbers of boards installed with Instacal: ' + str(board_list))
            board_num = int(input('\nEnter device number (default 0): ') or '0')
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

    channel = 0

    ai_props = AnalogInputProps(board_num)
    if ai_props.num_ai_chans < 1:
        util.print_unsupported_example(board_num)
        return

    separator = '\t'
    chan = 0
    print("\nChannels\n")
    for chan in range(0, ai_props.num_ai_chans):
        print(separator + str(chan), end = '')
        separator = ', '
    channel = int(input('\n\nChannel selected (default 0): ') or '0')
    util.clear_screen()

    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")
    print()

    index = 0
    for ai_range in ai_props.available_ranges:
        print(str(index) + ": ", ai_range, sep = " ")
        index += 1
    range_index = int(input('\nSelect range (default 0): ') or '0')
    util.clear_screen()
    ai_range = ai_props.available_ranges[range_index]
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")
    
    loop_count = int(input('\nEnter loop count (default 50): ') or '50')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id+ ")")
    try:
        for x in range(0, loop_count):
            # Get a value from the device
            if ai_props.resolution <= 16:
                # Use the a_in method for devices with a resolution <= 16
                value = ul.a_in(board_num, channel, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units(board_num, ai_range, value)
                fmt = '{:.3f}'
            else:
                # Use the a_in_32 method for devices with a resolution > 16
                # (optional parameter omitted)
                value = ul.a_in_32(board_num, channel, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units_32(board_num, ai_range, value)
                fmt = '{:.5f}'

            # Display the raw value
            util.clear_line(2, 2)
            util.print_at(2, 2, "Raw value: \t\t" + str(value))
            # Display the engineering value
            util.print_at(4, 2, "Engineering Value: \t" + fmt.format(eng_units_value))
            print()
            sleep(0.2)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
