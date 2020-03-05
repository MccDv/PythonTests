from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.enums import DigitalPortType
from console import util
from props.digital import DigitalProps
from mcculw.ul import ULError
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

    digital_props = DigitalProps(board_num)

    # Find the first port that supports input, defaulting to None
    # if one is not found.
    port = next(
        (port for port in digital_props.port_info
         if port.supports_output), None)
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
    port_index = int(input('\n\nChannel selected: '))
    port = digital_props.port_info[port_index]
        
    util.clear_screen()
    print("Device " + str(board_num) + " selected: " +
          device.product_name + " (" + device.unique_id + ")")
    print()
    try:
        # If the port is configurable, configure it for output.
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)

        bits = port.num_bits
        max_value = 2**bits - 1
        one_value = 0x5555

        port_value = max_value & one_value
        for x in range(0, 100):
            util.clear_line(2, 2)
            util.print_at(2, 2, 
                "Setting " + port.type.name + " to " + str(port_value))

            # Output the value to the port
            ul.d_out(board_num, port.type, port_value)

            bit_num = 0
            bit_value = 0
            index = 0
            
            bit_port = DigitalPortType.FIRSTPORTA
            if port.type < DigitalPortType.FIRSTPORTA:
                bit_port = DigitalPortType.AUXPORT
            for bit_num in range(bit_list[port_index], bit_list[port_index] + bits):
                bit_value = 2**index & port_value
                util.clear_line(4 + index, 2)
                util.print_at(4 + index, 2, bit_port.name + " bit " +
                      str(bit_num) + " value: " + str(bit_value))

                # Output the value to the bit
                ul.d_bit_out(board_num, bit_port, bit_num, bit_value)
                index += 1
            print()
            port_value = max_value & one_value
            one_value = one_value ^ max_value
            sleep(0.2)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
