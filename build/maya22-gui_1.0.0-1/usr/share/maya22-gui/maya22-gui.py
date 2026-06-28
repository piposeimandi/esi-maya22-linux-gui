import customtkinter as ctk
import subprocess
import json
import os
from PIL import Image

class AudioControlApp(ctk.CTk):
    CONFIG_FILE = 'config.json'

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title('MAYA22USB Control Panel')
        self.geometry('520x320')
        self.resizable(False, False)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'images', 'maya22-icon.png')
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            self.iconphoto(True, ctk.CTkImage(icon_img, size=(32, 32)))

        self.initUI()
        self.load_config()

    def initUI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---- INPUT SECTION ----
        input_frame = ctk.CTkFrame(self, corner_radius=10)
        input_frame.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=0)
        input_frame.grid_columnconfigure(1, weight=1)

        input_header = ctk.CTkLabel(input_frame, text="INPUT", font=ctk.CTkFont(size=15, weight="bold"))
        input_header.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")

        channels = [
            ("Line In", "line"),
            ("Mic", "mic"),
            ("Hi-Z", "hiz"),
            ("Mic Hi-Z", "mic_hiz"),
            ("Mute", "mute"),
        ]
        self.input_var = ctk.StringVar(value="line")
        for i, (text, value) in enumerate(channels):
            rb = ctk.CTkRadioButton(
                input_frame, text=text, variable=self.input_var,
                value=value, command=self.set_input_channel
            )
            rb.grid(row=i + 1, column=0, sticky="w", padx=(10, 0), pady=1)

        vol_font = ctk.CTkFont(size=12)
        ctk.CTkLabel(input_frame, text="L Vol", font=vol_font).grid(row=1, column=1, pady=(0, 0), sticky="s")
        self.input_slider_l = ctk.CTkSlider(input_frame, from_=0, to=127,
                                            command=self.set_input_left_volume)
        self.input_slider_l.grid(row=2, column=1, padx=(5, 15), pady=(0, 5), sticky="ew")

        ctk.CTkLabel(input_frame, text="R Vol", font=vol_font).grid(row=3, column=1, pady=(5, 0), sticky="s")
        self.input_slider_r = ctk.CTkSlider(input_frame, from_=0, to=127,
                                            command=self.set_input_right_volume)
        self.input_slider_r.grid(row=4, column=1, padx=(5, 15), pady=(0, 5), sticky="ew")

        self.monitor_var = ctk.BooleanVar(value=False)
        self.monitor_switch = ctk.CTkSwitch(
            input_frame, text="Monitor", variable=self.monitor_var,
            command=self.toggle_monitor
        )
        self.monitor_switch.grid(row=5, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="w")

        # ---- OUTPUT SECTION ----
        output_frame = ctk.CTkFrame(self, corner_radius=10)
        output_frame.grid(row=0, column=1, padx=(5, 15), pady=15, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=1)

        output_header = ctk.CTkLabel(output_frame, text="OUTPUT", font=ctk.CTkFont(size=15, weight="bold"))
        output_header.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")

        ctk.CTkLabel(output_frame, text="L Vol", font=vol_font).grid(row=1, column=0, pady=(0, 0), sticky="s")
        self.output_slider_l = ctk.CTkSlider(output_frame, from_=0, to=145,
                                             command=self.set_output_left_volume)
        self.output_slider_l.grid(row=2, column=0, padx=(10, 5), pady=(0, 5), sticky="ew")

        ctk.CTkLabel(output_frame, text="R Vol", font=vol_font).grid(row=1, column=1, pady=(0, 0), sticky="s")
        self.output_slider_r = ctk.CTkSlider(output_frame, from_=0, to=145,
                                             command=self.set_output_right_volume)
        self.output_slider_r.grid(row=2, column=1, padx=(5, 10), pady=(0, 5), sticky="ew")

        self.sync_var = ctk.BooleanVar(value=False)
        self.sync_switch = ctk.CTkSwitch(
            output_frame, text="Sync Outputs", variable=self.sync_var,
            command=self.save_config
        )
        self.sync_switch.grid(row=3, column=0, columnspan=2, pady=(12, 5), padx=10, sticky="w")

        self.mute_output_var = ctk.BooleanVar(value=False)
        self.mute_output_switch = ctk.CTkSwitch(
            output_frame, text="Mute Output", variable=self.mute_output_var,
            command=self.toggle_mute_output
        )
        self.mute_output_switch.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="w")

    def get_binary_path(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'maya22-control')

    def run_command(self, command):
        binary = self.get_binary_path()
        try:
            subprocess.run([binary] + command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] maya22-control: {e.stderr.strip()}")
        except FileNotFoundError:
            print(f"[ERROR] {binary} not found")

    def set_input_channel(self):
        channel = self.input_var.get().lower()
        self.run_command(['-c', channel])
        self.save_config()

    def set_input_left_volume(self, value):
        self.run_command(['-l', str(round(value))])
        self.save_config()

    def set_input_right_volume(self, value):
        self.run_command(['-r', str(round(value))])
        self.save_config()

    def set_output_left_volume(self, value):
        self.run_command(['-L', str(round(value))])
        if self.sync_var.get():
            self.output_slider_r.set(self.output_slider_l.get())
            self.run_command(['-R', str(round(value))])
        self.save_config()

    def set_output_right_volume(self, value):
        self.run_command(['-R', str(round(value))])
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
            'input_left_volume': self.input_slider_l.get(),
            'input_right_volume': self.input_slider_r.get(),
            'output_left_volume': self.output_slider_l.get(),
            'output_right_volume': self.output_slider_r.get(),
            'sync_outputs': self.sync_var.get(),
            'mute_output': self.mute_output_var.get(),
            'monitor': self.monitor_var.get(),
        }
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            print(f"[ERROR] saving config: {e}")

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self.input_var.set(config.get('input_channel', 'line'))
                self.input_slider_l.set(config.get('input_left_volume', 0))
                self.input_slider_r.set(config.get('input_right_volume', 0))
                self.output_slider_l.set(config.get('output_left_volume', 0))
                self.output_slider_r.set(config.get('output_right_volume', 0))
                self.sync_var.set(config.get('sync_outputs', False))
                self.mute_output_var.set(config.get('mute_output', False))
                self.monitor_var.set(config.get('monitor', False))
            except (json.JSONDecodeError, OSError) as e:
                print(f"[ERROR] loading config: {e}")

if __name__ == '__main__':
    app = AudioControlApp()
    app.mainloop()
