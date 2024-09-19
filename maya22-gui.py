import tkinter as tk
from tkinter import ttk
import subprocess
import json
import os

class AudioControlApp(tk.Tk):
    CONFIG_FILE = 'config.json'

    def __init__(self):
        super().__init__()
        self.title('MAYA22USB Control Panel')
        self.initUI()
        self.load_config()

    def initUI(self):
        # Center the window
        self.geometry('350x250')
        self.eval('tk::PlaceWindow . center')

        # Input Section
        input_frame = ttk.LabelFrame(self, text='INPUT')
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='n')

        self.input_var = tk.StringVar(value="Line In")  # Default to Line In
        self.line_in_radio = ttk.Radiobutton(input_frame, text='Line In', variable=self.input_var, value='line', command=self.set_input_channel)
        self.line_in_radio.grid(row=0, column=0, sticky='w')
        self.mic_radio = ttk.Radiobutton(input_frame, text='Mic', variable=self.input_var, value='mic', command=self.set_input_channel)
        self.mic_radio.grid(row=1, column=0, sticky='w')
        self.hiz_radio = ttk.Radiobutton(input_frame, text='Hi-Z', variable=self.input_var, value='hiz', command=self.set_input_channel)
        self.hiz_radio.grid(row=2, column=0, sticky='w')
        self.hiz_radio = ttk.Radiobutton(input_frame, text='Mic Hi-Z', variable=self.input_var, value='mic_hiz', command=self.set_input_channel)
        self.hiz_radio.grid(row=3, column=0, sticky='w')
        self.hiz_radio = ttk.Radiobutton(input_frame, text='Mute', variable=self.input_var, value='mute', command=self.set_input_channel)
        self.hiz_radio.grid(row=4, column=1, sticky='w')

        # Monitor button as a CheckButton
        self.monitor_var = tk.BooleanVar()
        self.monitor_button = ttk.Checkbutton(input_frame, text='Monitor', variable=self.monitor_var, command=self.toggle_monitor)
        self.monitor_button.grid(row=4, column=2, padx=5)

        # Volume sliders for Input
        self.input_slider_1 = ttk.Scale(input_frame, from_=127, to=0, orient='vertical', command=self.set_input_left_volume)
        self.input_slider_1.grid(row=0, column=1, rowspan=3, padx=10)
        self.input_slider_2 = ttk.Scale(input_frame, from_=127, to=0, orient='vertical', command=self.set_input_right_volume)
        self.input_slider_2.grid(row=0, column=2, rowspan=3, padx=10)



        # Output Section
        output_frame = ttk.LabelFrame(self, text='OUTPUT')
        output_frame.grid(row=0, column=2, padx=10, pady=10, sticky='n')

        # Volume sliders for Output
        self.output_slider_1 = ttk.Scale(output_frame, from_=145, to=0, orient='vertical', command=self.set_output_left_volume)
        self.output_slider_1.grid(row=0, column=0, padx=10)

        self.output_slider_2 = ttk.Scale(output_frame, from_=145, to=0, orient='vertical', command=self.set_output_right_volume)
        self.output_slider_2.grid(row=0, column=1, padx=10)

        # Sync checkbox
        self.sync_var = tk.BooleanVar()
        self.sync_check = ttk.Checkbutton(output_frame, text='Sync Outputs', variable=self.sync_var, command=self.save_config)
        self.sync_check.grid(row=1, column=0, columnspan=2, pady=5)

        self.mute_output_var = tk.BooleanVar()
        self.mute_output_button = ttk.Checkbutton(output_frame, text='Mute Output', variable=self.mute_output_var, command=self.toggle_mute_output)
        self.mute_output_button.grid(row=2, column=0,columnspan=2, pady=5)


    def run_command(self, command):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        command_path = os.path.join(script_dir, 'maya22-control')
        subprocess.run(['maya22-control'] + command)

    def set_input_channel(self):
        channel = self.input_var.get().lower()
        self.run_command(['-c', channel])
        self.save_config()

    def set_input_left_volume(self, value):
        self.run_command(['-l', str(int(float(value)))])
        self.save_config()

    def set_input_right_volume(self, value):
        self.run_command(['-r', str(int(float(value)))])
        self.save_config()

    def set_output_left_volume(self, value):
        self.run_command(['-L', str(int(float(value)))])
        if self.sync_var.get():
            self.output_slider_2.set(self.output_slider_1.get())
            self.run_command(['-R', str(int(float(value)))])
        self.save_config()

    def set_output_right_volume(self, value):
        self.run_command(['-R', str(int(float(value)))])
        self.save_config()

    def toggle_mute_output(self):
        if self.mute_output_var.get():
            self.run_command(['-I'])
        else:
            self.run_command(['-i'])
        self.save_config()

    def toggle_monitor(self):
        if self.monitor_var.get():
            self.run_command(['-M'])
        else:
            self.run_command(['-m'])
        self.save_config()

    def save_config(self):
        config = {
            'input_channel': self.input_var.get(),
            'input_left_volume': self.input_slider_1.get(),
            'input_right_volume': self.input_slider_2.get(),
            'output_left_volume': self.output_slider_1.get(),
            'output_right_volume': self.output_slider_2.get(),
            'sync_outputs': self.sync_var.get(),
            'mute_output': self.mute_output_var.get(),
            'monitor': self.monitor_var.get()
        }
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Restore values from config
                self.input_var.set(config.get('input_channel', 'line'))
                self.input_slider_1.set(config.get('input_left_volume', 0))
                self.input_slider_2.set(config.get('input_right_volume', 0))
                self.output_slider_1.set(config.get('output_left_volume', 0))
                self.output_slider_2.set(config.get('output_right_volume', 0))
                self.sync_var.set(config.get('sync_outputs', False))
                self.mute_output_var.set(config.get('mute_output', False))
                self.monitor_var.set(config.get('monitor', False))

app = AudioControlApp()
app.mainloop()

