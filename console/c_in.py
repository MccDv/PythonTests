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
    use_device_detection = False
    board_num = 1

    try:
        if use_device_detection:
            #type_list = [122, 197, 303, 310, 311, 318]
            type_list = [310]
            config_first_detected_device(board_num, type_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_counters:
            raise Exception('Error: The DAQ device does not support counters')

        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ctr_info = daq_dev_info.get_ctr_info()

        # Use the first counter channel on the board (some boards start channel
        # numbering at 1 instead of 0, the CtrInfo class is used here to find
        # the first one).
        counter_num = ctr_info.chan_info[0].channel_num

        #ul.c_clear(board_num, counter_num)
        # Get a value from the device
        value = ul.c_in_32(board_num, counter_num)
        # Display the value
        print('Counter Value:', value)
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
