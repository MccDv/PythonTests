from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_double

from mcculw import ul
from mcculw.enums import (ScanOptions, ULRange, InfoType, BoardInfo, AiChanType,
                          AnalogInputMode, TcType, TempScale)
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
    board_num = 2
    low_chan = 0
    high_chan = 3
    num_chans = high_chan - low_chan + 1
    # Supported PIDs for the USB-2408 and USB-2416 Series
    # USB-2408 = 253, USB-2408-2AO = 254, USB-2416 = 208, USB-2416-4AO = 209
    supported_pids = [253, 254, 208, 209]
    memhandle = None

    try:
        if use_device_detection:
            config_first_detected_device(board_num, supported_pids)

        daq_dev_info = DaqDeviceInfo(board_num)
        print('\nDevice selected: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        rate = 10
        points_per_channel = 10
        total_count = points_per_channel * num_chans

        scan_options = ScanOptions.FOREGROUND | ScanOptions.SCALEDATA

        memhandle = ul.scaled_win_buf_alloc(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array_scaled method for scaled buffers.
        ctypes_array = cast(memhandle, POINTER(c_double))
        # Note: the ctypes array will no longer be valid after win_buf_free is
        # called.
        # A copy of the buffer can be created using win_buf_to_array or
        # win_buf_to_array_32 before the memory is freed. The copy can be used
        # at any time.

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Error: Failed to allocate memory')

        # Set channel settings
        set_channel_settings(board_num)

        # Start the scan
        ul.a_in_scan(board_num, low_chan, high_chan, total_count,
                     rate, ULRange.BIP10VOLTS, memhandle, scan_options)

        print('Scan completed successfully. Data:')

        # Create a format string that aligns the data in columns
        row_format = '{:>5}' + '{:>10}' * num_chans

        # Print the channel name headers
        labels = ['Index']
        for ch_num in range(low_chan, high_chan + 1):
            labels.append('CH' + str(ch_num))
        print(row_format.format(*labels))

        # Print the data
        for index in range(points_per_channel):
            display_data = [index]
            for data_index in range(num_chans):
                display_data.append('{:.3f}'.format(ctypes_array[data_index]))
            # Print this row
            print(row_format.format(*display_data))
    except Exception as e:
        print('\n', e)
    finally:
        # Free the buffer in a finally block to prevent a memory leak.
        if memhandle:
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


def set_channel_settings(board_num):
    channel = 0
    # Set channel type to voltage
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                  AiChanType.VOLTAGE)
    # Set to differential input mode
    ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
    # Set data rate to 1000Hz
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE,
                  1000)

    channel = 1
    # Set channel type to voltage
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                  AiChanType.VOLTAGE)
    # Set to single-ended input mode
    ul.a_chan_input_mode(board_num, channel, AnalogInputMode.SINGLE_ENDED)
    # Set data rate to 1000Hz
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE,
                  1000)

    channel = 2
    # Set channel type to TC (thermocouple)
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                  AiChanType.TC)
    # Set thermocouple type to type J
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.CHANTCTYPE,
                  TcType.T)
    # Set the temperature scale to Fahrenheit
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.TEMPSCALE,
                  TempScale.FAHRENHEIT)
    # Set data rate to 60Hz
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE,
                  60)

    channel = 3
    # Set channel type to TC (thermocouple)
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                  AiChanType.TC)
    # Set thermocouple type to type K
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.CHANTCTYPE,
                  TcType.K)
    # Set the temperature scale to Fahrenheit
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.TEMPSCALE,
                  TempScale.FAHRENHEIT)
    # Set data rate to 60Hz
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE,
                  60)


if __name__ == '__main__':
    run_example()
