import ctypes
from ctypes import *
import os
import sys

from mcculw import ul
from mcculw.enums import InterfaceType

STD_OUTPUT_HANDLE = -11

class COORD(Structure):
    pass
 
COORD._fields_ = [("X", c_short), ("Y", c_short)]
 
def detect_devices():
    """Adds the first available device to the UL.

    Parameters
    ----------
    board_num : int, optional
        The board number to assign to the board when configuring the device.

    Returns
    -------
    boolean
        True if a device was found and added, False if no devices were
        found. 
    """

    # Get the device inventory
    devices = ul.get_daq_device_inventory(InterfaceType.ANY)
    # Check if any devices were found
    if len(devices) > 0:
        for x in range(0, len(devices)):
            device = devices[x]
            print("Device " + str(x) + ": " + device.product_name +
                  " (" + device.unique_id + ")")

    return devices


def config_first_detected_device_of_type(board_num, types_list):
    """Adds the first available device to the UL.

    Parameters
    ----------
    board_num : int, optional
        The board number to assign to the board when configuring the device.

    Returns
    -------
    boolean
        True if a device was found and added, False if no devices were
        found. 
    """

    # Get the device inventory (optional parameter omitted)
    devices = ul.get_daq_device_inventory(InterfaceType.ANY)

    device = next((device for device in devices
                   if device.product_id in types_list), None)

    if device != None:
        # Print a messsage describing the device found
        print("Found device: " + device.product_name +
              " (" + device.unique_id + ")\n")
        # Add the device to the UL.
        ul.create_daq_device(board_num, device)
        return True

    return False


def print_ul_error(ul_error):
    print("A UL Error occurred.\nError Code: " + str(ul_error.errorcode)
          + "\nMessage: " + ul_error.message)


def print_unsupported_example(board_num):
    print("Board " + str(board_num)
          + " was not found or is not compatible with this example.")


def memhandle_as_ctypes_array(memhandle):
    return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ushort))


def memhandle_as_ctypes_array_32(memhandle):
    return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong))


def memhandle_as_ctypes_array_scaled(memhandle):
    return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_double))

def print_at(r, c, s):
    h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    windll.kernel32.SetConsoleCursorPosition(h, COORD(c, r))

    c = s.encode("windows-1252")
    windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)

def clear_line(r, c):
    h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    windll.kernel32.SetConsoleCursorPosition(h, COORD(c, r))

    clr_line = " " * 48
    c = clr_line.encode("windows-1252")
    windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)

def clear_screen():
    os.system('CLS')
