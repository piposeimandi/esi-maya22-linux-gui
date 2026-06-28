#!/usr/bin/env python3

import customtkinter as ctk
import tkinter.messagebox as mb
import subprocess
import json
import os
from PIL import Image

# --- System Tray via StatusNotifierItem (KDE/GNOME) ---
HAS_TRAY = False
_tray_indicator = None  # AyatanaAppIndicator3 instance

try:
    import gi
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3, Gtk, GLib
    HAS_TRAY = True
except (ImportError, ValueError):
    try:
        import gi
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as AyatanaAppIndicator3, Gtk, GLib
        HAS_TRAY = True
    except (ImportError, ValueError):
        pass


class AudioControlApp(ctk.CTk):
    CONFIG_FILE = 'config.json'

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._tray_active = False

        self.title('MAYA22USB Control Panel')
        self.geometry('660x400')
        self.resizable(False, False)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = script_dir
        icon_path = os.path.join(script_dir, 'images', 'maya22-icon.png')
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            self.iconphoto(True, ctk.CTkImage(icon_img, size=(32, 32)))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.initUI()
        self.load_config()

    # ===================== UI =====================

    def initUI(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # ----- LEFT: Input Selection -----
        sel_frame = ctk.CTkFrame(self, corner_radius=10)
        sel_frame.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="ns")
        sel_header = ctk.CTkLabel(sel_frame, text="Input",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        sel_header.grid(row=0, column=0, pady=(12, 8), padx=15)

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
                sel_frame, text=text, variable=self.input_var,
                value=value, command=self.set_input_channel,
                font=ctk.CTkFont(size=12)
            )
            rb.grid(row=i + 1, column=0, sticky="w", padx=15, pady=2)

        sel_frame.grid_rowconfigure(len(channels) + 1, weight=1)

        # ----- MIDDLE: INPUT -----
        in_frame = ctk.CTkFrame(self, corner_radius=10)
        in_frame.grid(row=0, column=1, padx=5, pady=15, sticky="nsew")
        in_frame.grid_columnconfigure(0, weight=1)
        in_frame.grid_columnconfigure(1, weight=1)
        in_frame.grid_rowconfigure(3, weight=1)

        in_header = ctk.CTkLabel(in_frame, text="INPUT",
                                 font=ctk.CTkFont(size=14, weight="bold"))
        in_header.grid(row=0, column=0, columnspan=2, pady=(12, 0))

        vol_font = ctk.CTkFont(size=11)
        ctk.CTkLabel(in_frame, text="L", font=vol_font).grid(row=1, column=0)
        ctk.CTkLabel(in_frame, text="R", font=vol_font).grid(row=1, column=1)

        self.input_slider_l = ctk.CTkSlider(
            in_frame, from_=0, to=127, orientation="vertical",
            height=160, command=self.set_input_left_volume
        )
        self.input_slider_l.grid(row=2, column=0, padx=(15, 5), pady=2, sticky="ns")

        self.input_slider_r = ctk.CTkSlider(
            in_frame, from_=0, to=127, orientation="vertical",
            height=160, command=self.set_input_right_volume
        )
        self.input_slider_r.grid(row=2, column=1, padx=(5, 15), pady=2, sticky="ns")

        ctrl_font = ctk.CTkFont(size=11)
        self.input_mute_var = ctk.BooleanVar(value=False)

        in_controls = ctk.CTkFrame(in_frame, fg_color="transparent")
        in_controls.grid(row=3, column=0, columnspan=2, pady=(6, 10))
        in_controls.grid_columnconfigure((0, 1, 2), weight=1)

        self.mute_in_switch = ctk.CTkSwitch(
            in_controls, text="Mute", variable=self.input_mute_var,
            command=self.toggle_mute_input, font=ctrl_font
        )
        self.mute_in_switch.grid(row=0, column=0, padx=2)

        self.input_sync_var = ctk.BooleanVar(value=False)
        self.input_sync_switch = ctk.CTkSwitch(
            in_controls, text="L/R", variable=self.input_sync_var,
            command=self.save_config, font=ctrl_font
        )
        self.input_sync_switch.grid(row=0, column=1, padx=2)

        self.monitor_var = ctk.BooleanVar(value=False)
        self.monitor_switch = ctk.CTkSwitch(
            in_controls, text="Mon", variable=self.monitor_var,
            command=self.toggle_monitor, font=ctrl_font
        )
        self.monitor_switch.grid(row=0, column=2, padx=2)

        # ----- RIGHT: OUTPUT -----
        out_frame = ctk.CTkFrame(self, corner_radius=10)
        out_frame.grid(row=0, column=2, padx=(5, 15), pady=15, sticky="nsew")
        out_frame.grid_columnconfigure(0, weight=1)
        out_frame.grid_columnconfigure(1, weight=1)
        out_frame.grid_rowconfigure(3, weight=1)

        out_header = ctk.CTkLabel(out_frame, text="OUTPUT",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        out_header.grid(row=0, column=0, columnspan=2, pady=(12, 0))

        ctk.CTkLabel(out_frame, text="L", font=vol_font).grid(row=1, column=0)
        ctk.CTkLabel(out_frame, text="R", font=vol_font).grid(row=1, column=1)

        self.output_slider_l = ctk.CTkSlider(
            out_frame, from_=0, to=145, orientation="vertical",
            height=160, command=self.set_output_left_volume
        )
        self.output_slider_l.grid(row=2, column=0, padx=(15, 5), pady=2, sticky="ns")

        self.output_slider_r = ctk.CTkSlider(
            out_frame, from_=0, to=145, orientation="vertical",
            height=160, command=self.set_output_right_volume
        )
        self.output_slider_r.grid(row=2, column=1, padx=(5, 15), pady=2, sticky="ns")

        out_controls = ctk.CTkFrame(out_frame, fg_color="transparent")
        out_controls.grid(row=3, column=0, columnspan=2, pady=(6, 10))
        out_controls.grid_columnconfigure((0, 1), weight=1)

        self.sync_var = ctk.BooleanVar(value=False)
        self.sync_switch = ctk.CTkSwitch(
            out_controls, text="Sync", variable=self.sync_var,
            command=self.save_config, font=ctrl_font
        )
        self.sync_switch.grid(row=0, column=0, padx=2)

        self.mute_output_var = ctk.BooleanVar(value=False)
        self.mute_output_switch = ctk.CTkSwitch(
            out_controls, text="Mute", variable=self.mute_output_var,
            command=self.toggle_mute_output, font=ctrl_font
        )
        self.mute_output_switch.grid(row=0, column=1, padx=2)

    # ===================== helpers =====================

    def get_binary_path(self):
        return os.path.join(self.script_dir, 'maya22-control')

    def run_command(self, command):
        binary = self.get_binary_path()
        try:
            subprocess.run([binary] + command, check=True,
                           capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] maya22-control: {e.stderr.strip()}")
        except FileNotFoundError:
            print(f"[ERROR] {binary} not found")

    # ===================== callbacks =====================

    def set_input_channel(self):
        channel = self.input_var.get().lower()
        self.run_command(['-c', channel])
        self.save_config()

    def toggle_mute_input(self):
        if self.input_mute_var.get():
            self.input_slider_l.set(0)
            self.input_slider_r.set(0)
            self.run_command(['-l', '0'])
            self.run_command(['-r', '0'])
        else:
            self.run_command(['-l', str(round(self.input_slider_l.get()))])
            self.run_command(['-r', str(round(self.input_slider_r.get()))])
        self.save_config()

    def set_input_left_volume(self, value):
        self.run_command(['-l', str(round(value))])
        if self.input_sync_var.get():
            self.input_slider_r.set(self.input_slider_l.get())
            self.run_command(['-r', str(round(value))])
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

    # ===================== close / tray =====================

    def on_closing(self):
        if HAS_TRAY:
            r = mb.askyesnocancel(
                title="MAYA22USB",
                message="What do you want to do?",
                detail="Yes = Close app\nNo = Minimize to tray\nCancel = Keep open"
            )
            if r is None:
                return
            if r:
                self.quit_app()
            else:
                self.minimize_to_tray()
        else:
            if mb.askokcancel("MAYA22USB", "Close the application?"):
                self.quit_app()

    def minimize_to_tray(self):
        self.withdraw()
        self._start_tray()

    def show_window(self, *args):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self):
        self._stop_tray()
        self.destroy()

    # ----- tray via StatusNotifierItem (AppIndicator) -----

    def _start_tray(self):
        global _tray_indicator
        if not HAS_TRAY or _tray_indicator is not None:
            return

        # Look for icon in several locations
        icon_name = "maya22-gui"
        for p in [
            os.path.join(self.script_dir, 'images', 'maya22-icon.png'),
            '/usr/share/icons/hicolor/256x256/apps/maya22-gui.png',
            '/usr/share/icons/hicolor/scalable/apps/maya22-gui.svg',
        ]:
            if os.path.exists(p):
                icon_name = p
                break

        _tray_indicator = AyatanaAppIndicator3.Indicator.new(
            "maya22-gui", icon_name,
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        _tray_indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)

        # Build menu
        menu = Gtk.Menu()

        item_show = Gtk.MenuItem(label="Show")
        item_show.connect("activate", lambda w: self.show_window())
        menu.append(item_show)

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda w: self.quit_app())
        menu.append(item_quit)

        menu.show_all()
        _tray_indicator.set_menu(menu)

        # Pump GTK events periodically (needed for menu to work)
        self._tray_poll()

    def _tray_poll(self):
        if _tray_indicator is None:
            return
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.after(50, self._tray_poll)

    def _stop_tray(self):
        global _tray_indicator
        if _tray_indicator is not None:
            _tray_indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.PASSIVE)
            _tray_indicator = None

    # ===================== config persistence =====================

    def save_config(self):
        config = {
            'input_channel': self.input_var.get(),
            'input_left_volume': self.input_slider_l.get(),
            'input_right_volume': self.input_slider_r.get(),
            'output_left_volume': self.output_slider_l.get(),
            'output_right_volume': self.output_slider_r.get(),
            'input_sync': self.input_sync_var.get(),
            'sync_outputs': self.sync_var.get(),
            'mute_output': self.mute_output_var.get(),
            'mute_input': self.input_mute_var.get(),
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
                self.input_sync_var.set(config.get('input_sync', False))
                self.sync_var.set(config.get('sync_outputs', False))
                self.mute_output_var.set(config.get('mute_output', False))
                self.input_mute_var.set(config.get('mute_input', False))
                self.monitor_var.set(config.get('monitor', False))
            except (json.JSONDecodeError, OSError) as e:
                print(f"[ERROR] loading config: {e}")


if __name__ == '__main__':
    app = AudioControlApp()
    app.mainloop()
