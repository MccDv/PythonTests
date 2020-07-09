from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import TempScale
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
    use_device_detection = False
    board_num = 0

    try:
        if use_device_detection:
            #type_list = [122, 197, 254, 303, 310, 311, 318]
            type_list = [197]
            config_first_detected_device(board_num, type_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ai_info = daq_dev_info.get_ai_info()
        if ai_info.num_temp_chans <= 0:
            raise Exception('Error: The DAQ device does not support '
                            'temperature input')
        channel = 0

        # Get the value from the device (optional parameters omitted)
        value = ul.t_in(board_num, channel, TempScale.CELSIUS)

        # Display the value
        print('Channel', channel, 'Value (deg C):', value)
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
