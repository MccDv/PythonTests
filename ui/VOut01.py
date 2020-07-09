"""
File:                       VOut01.py

Library Call Demonstrated:  mcculw.ul.v_out()

Purpose:                    Writes to a D/A Output Channel.

Demonstration:              Sends a digital output to D/A 0.

Special Requirements:       Device must have a D/A converter.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error, validate_float_entry
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error, validate_float_entry


class VOut01(UIExample):
    def __init__(self, master=None):
        super(VOut01, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            device_info = DaqDeviceInfo(self.board_num)
            self.ao_info = device_info.get_ao_info()
            if self.ao_info.is_supported and self.ao_info.supports_v_out:
                self.create_widgets()
                dev_name = device_info.product_name
                self.device_label["text"] = (str(self.board_num)
                    + ") " + dev_name)
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()
        ao_range = self.ao_info.supported_ranges[0]
        data_value = self.get_data_value()

        try:
            # Send the value to the device (optional parameter omitted)
            ul.v_out(self.board_num, channel, ao_range, data_value)
        except ULError as e:
            show_ul_error(e)

    def get_data_value(self):
        try:
            return float(self.data_value_entry.get())
        except ValueError:
            return 0

    def get_channel_num(self):
        if self.ao_info.num_chans == 1:
            return 0
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if value < 0 or value > self.ao_info.num_chans - 1:
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        channel_vcmd = self.register(self.validate_channel_entry)
        float_vcmd = self.register(validate_float_entry)

        curr_row = 0
        self.device_label = tk.Label(main_frame)
        if self.ao_info.num_chans > 1:
            channel_entry_label = tk.Label(main_frame)
            channel_entry_label["text"] = "Channel Number:"
            channel_entry_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.channel_entry = tk.Spinbox(
                main_frame, from_=0, to=max(self.ao_info.num_chans - 1, 0),
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.channel_entry.grid(row=curr_row, column=1, sticky=tk.W)
            self.device_label.grid(row=curr_row, column=2, sticky=tk.W)
            curr_row += 1
        else:
            self.device_label.grid(row=curr_row, column=0, sticky=tk.W)

        data_value_label = tk.Label(main_frame)
        data_value_label["text"] = "Value (V):"
        data_value_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.data_value_entry = tk.Entry(
            main_frame, validate='key', validatecommand=(float_vcmd, '%P'))
        self.data_value_entry.grid(row=curr_row, column=1, sticky=tk.W)
        self.data_value_entry.insert(0, "0")

        update_button = tk.Button(main_frame)
        update_button["text"] = "Update"
        update_button["command"] = self.update_value
        update_button.grid(row=curr_row, column=2, padx=3, pady=3)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    VOut01(master=tk.Tk()).mainloop()
