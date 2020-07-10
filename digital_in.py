from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.enums import BoardInfo, InfoType, DigitalPortType
import util
from props.digital import DigitalProps
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

    digital_props = DigitalProps(board_num)

    # Find the first port that supports input, defaulting to None
    # if one is not found.
    port = next(
        (port for port in digital_props.port_info
         if port.supports_input), None)
    if port == None:
        util.print_unsupported_example(board_num)
        return

    index = 0
    first_bit = 0
    bit_list = []
    print()
    for port in digital_props.port_info:
        print(str(index) + ') ', end = '')
        print(port.type)
        if index > 0 and (port.type == DigitalPortType.FIRSTPORTA):
            first_bit = 0
        bit_list.append(first_bit)
        first_bit = port.num_bits + bit_list[index]
        index += 1
    port_index = int(input('\n\nChannel selected (default 0): ') or '0')
    port = digital_props.port_info[port_index]
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")

    loop_count = int(input('\nEnter loop count (default 50): ') or '50')
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          prod_name + " (" + prod_id + ")")
    print()
    try:
        # If the port is configurable, configure it for input.
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.IN)
            #util.print_at(16, 2, 'Configured for input ' + \
             #     str(board_num) + str(port.type) + \
              #    str(DigitalIODirection.IN))

        for x in range(0, loop_count):
            # Get a value from the digital port
            port_value = ul.d_in(board_num, port.type)
            # Display the port value
            util.clear_line(2, 2)
            util.print_at(2, 2, port.type.name + " value: \t" + str(port_value))

            # Get a value from the first digital bit
            index = 0
            bits = port.num_bits
            bit_port = DigitalPortType.FIRSTPORTA
            if port.type < DigitalPortType.FIRSTPORTA:
                bit_port = DigitalPortType.AUXPORT
            for bit_num in range(bit_list[port_index], bit_list[port_index] + bits):
                bit_value = ul.d_bit_in(board_num, bit_port, bit_num)
                # Display the bit value
                util.clear_line(4 + index, 2)
                util.print_at(4 + index, 2, "  Bit " + str(bit_num) + " value: \t" + str(bit_value))
                index += 1
            print()
            sleep(0.2)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
