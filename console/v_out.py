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
            #type_list = [120, 310, 197, 303, 311]
            type_list = []
            config_first_detected_device(board_num, type_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_output:
            raise Exception('Error: The DAQ device does not support '
                            'analog output')

        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ao_info = daq_dev_info.get_ao_info()
        ao_range = ao_info.supported_ranges[0]
        channel = 0

        data_value = ao_range.range_max / 2

        print('Outputting', data_value, 'Volts to channel', channel)
        # Send the value to the device (optional parameter omitted)
        ul.v_out(board_num, channel, ao_range, data_value)
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
