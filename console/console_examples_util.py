from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import InterfaceType


def config_first_detected_device(board_num, types_list=None):
    """Adds the first available device to the UL.  If a types_list is specified,
    the first available device in the types list will be add to the UL.

    Parameters
    ----------
    board_num : int
        The board number to assign to the board when configuring the device.

    types_list : list[int], optional
        A list of product IDs used to filter the results. Default is None.
    """
    ul.ignore_instacal()
    devices = ul.get_daq_device_inventory(InterfaceType.ANY)
    if not devices:
        raise Exception('Error: No DAQ devices found')

    print('Found', len(devices), 'DAQ device(s):')
    for device in devices:
        print('  ', device.product_name, ' (', device.unique_id, ')',
              '\t device type = ', device.product_id, sep='')

    device = devices[0]
    if types_list:
        device = next((device for device in devices
                       if device.product_id in types_list), None)
        if not device:
            raise Exception('Error: No DAQ device found that is included '
                            'in list provided.')

    # Add the first DAQ device to the UL with the specified board number
    ul.create_daq_device(board_num, device)



