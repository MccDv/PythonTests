from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device


def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed.
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    board_num = 0

    try:
        if use_device_detection:
            #type_list = [122, 197, 254, 303, 310, 311, 318]
            type_list = [303]
            config_first_detected_device(board_num, type_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ai_info = daq_dev_info.get_ai_info()
        ai_range = ai_info.supported_ranges[0]
        channel = 0

        # Get a value from the device
        if ai_info.resolution <= 16:
            # Use the a_in method for devices with a resolution <= 16
            value = ul.a_in(board_num, channel, ai_range)
            # Convert the raw value to engineering units
            eng_units_value = ul.to_eng_units(board_num, ai_range, value)
        else:
            # Use the a_in_32 method for devices with a resolution > 16
            # (optional parameter omitted)
            value = ul.a_in_32(board_num, channel, ai_range)
            # Convert the raw value to engineering units
            eng_units_value = ul.to_eng_units_32(board_num, ai_range, value)

        # Display the raw value
        print('Raw Value:', value)
        # Display the engineering value
        print('Engineering Value: {:.3f}'.format(eng_units_value))
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
