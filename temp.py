import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

CONFIG_FILE = 'config.json'
TRANSLATIONS_FILE = 'translations.json'

# Default language
current_language = "en"

# Load translations from a JSON file
def load_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default to English if translation file does not exist
        return {
            "en": {
                "select_input_channel": "Select input channel",
                "input_volume": "Input Volume",
                "left": "Left",
                "right": "Right",
                "output_volume": "Output Volume",
                "sync_volumes": "Sync output volumes",
                "activate_monitoring": "Activate monitoring",
                "enable_headphones": "Enable headphones"
            }
        }

# Load translations
translations = load_translations()

# Execute commands
def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        return output
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error executing command '{cmd}': {e.output.decode()}")
        return None

# Sync output volumes
def sync_volumes():
    if sync_var.get() == 1:
        # Sync the right output volume with the left
        output_vol_right.set(output_vol_left.get())
        run_command(f"./maya22-control -R {output_vol_right.get()}")
    else:
        run_command(f"./maya22-control -R {output_vol_right.get()}")

def update_output_volume(side, val):
    if side == 'L':
        run_command(f"./maya22-control -L {val}")
    elif side == 'R':
        run_command(f"./maya22-control -R {val}")

    # If synchronization is active, update the other slider
    if sync_var.get() == 1:
        if side == 'L':
            output_vol_right.set(val)
        elif side == 'R':
            output_vol_left.set(val)
    
    save_settings()

def update_slider_volumes():
    if sync_var.get() == 1:
        output_vol_right.set(output_vol_left.get())

# Toggle monitoring on/off
def toggle_monitoring():
    if monitoring_var.get() == 1:
        result = run_command("./maya22-control -M")  # Activate monitoring
        if result is not None:
            print("Info", "Monitoring activated.")
    else:
        result = run_command("./maya22-control -m")  # Deactivate monitoring
        if result is not None:
            print("Info", "Monitoring deactivated.")
    save_settings()

# Toggle headphones on/off
def toggle_headphones():
    if headphone_var.get() == 1:
        result = run_command("./maya22-control -i")  # Enable headphones
        if result is not None:
            print("Info", "Headphones enabled.")
    else:
        result = run_command("./maya22-control -I")  # Disable headphones
        if result is not None:
            print("Info", "Headphones disabled.")
    save_settings()

# Save settings to a file
def save_settings():
    settings = {
        'headphones_enabled': headphone_var.get(),
        'monitoring_enabled': monitoring_var.get(),
        'input_vol_left': input_vol_left.get(),
        'input_vol_right': input_vol_right.get(),
        'output_vol_left': output_vol_left.get(),
        'output_vol_right': output_vol_right.get(),
        'input_channel': input_channel.get(),
        'language': current_language,  # Save selected language
        'sync_volumes': sync_var.get()  # Save sync status
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f)
    except IOError as e:
        messagebox.showerror("Error", f"Error saving settings: {e}")

# Load settings from the file
def load_current_settings():
    global current_language
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            
        # Apply loaded values
        headphone_var.set(settings.get('headphones_enabled', 0))
        monitoring_var.set(settings.get('monitoring_enabled', 0))
        input_vol_left.set(settings.get('input_vol_left', 0))
        input_vol_right.set(settings.get('input_vol_right', 0))
        output_vol_left.set(settings.get('output_vol_left', 0))
        output_vol_right.set(settings.get('output_vol_right', 0))
        input_channel.set(settings.get('input_channel', 'mic'))  # Set input channel
        current_language = settings.get('language', 'en')  # Load selected language
        sync_var.set(settings.get('sync_volumes', 0))  # Load sync status
        update_texts()  # Update interface texts
        update_slider_volumes()  # Update synced volumes if needed

    except FileNotFoundError:
        # Initialize with default values if the file does not exist
        headphone_var.set(0)
        monitoring_var.set(0)
        input_vol_left.set(0)
        input_vol_right.set(0)
        output_vol_left.set(0)
        output_vol_right.set(0)
        input_channel.set('mic')  # Default input channel
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error reading configuration file.")
    except Exception as e:
        messagebox.showerror("Error", f"Error loading configuration: {e}")

# Update interface texts based on the language
def update_texts():
    lang = translations.get(current_language, translations["en"])
    input_channel_label.config(text=lang["select_input_channel"])
    input_frame.config(text=lang["input_volume"])
    output_frame.config(text=lang["output_volume"])
    sync_check.config(text=lang["sync_volumes"])
    monitoring_check.config(text=lang["activate_monitoring"])
    headphone_check.config(text=lang["enable_headphones"])

    # Adjust window size to fit the content
    window.update_idletasks()
    window.geometry(f"{window.winfo_reqwidth()}x{window.winfo_reqheight()}")

# Change language
def change_language(lang):
    global current_language
    current_language = lang
    update_texts()
    save_settings()

# Functions to adjust volumes
def set_input_volume(side, val):
    if side == 'l':
        result = run_command(f"./maya22-control -l {val}")
        if result is not None:
            print("Info", "Input volume (Left) updated.")
    elif side == 'r':
        result = run_command(f"./maya22-control -r {val}")
        if result is not None:
            print("Info", "Input volume (Right) updated.")
    save_settings()

def set_output_volume(side, val):
    if side == 'L':
        output_vol_left.set(val)
        update_output_volume('L', val)
    elif side == 'R':
        output_vol_right.set(val)
        update_output_volume('R', val)
    save_settings()

# Create window
window = tk.Tk()
window.title("Control ESI Maya22")

# Adjust window size and position to center it on the screen
def center_window(window, width, height):
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Ensure the window does not exceed screen dimensions
    if width > screen_width:
        width = screen_width
    if height > screen_height:
        height = screen_height
    
    # Calculate the position for centering the window
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    
    # Set the window size and position
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

# Center window on the screen
center_window(window, 400, 600)  # Adjust window size as needed

# Create main frame
main_frame = ttk.Frame(window, padding="10")
main_frame.grid(row=0, column=0, sticky="nsew")

# Language selector
language_frame = ttk.LabelFrame(main_frame, text="Language", padding="10")
language_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

# Add buttons for changing languages (example)
ttk.Button(language_frame, text="English", command=lambda: change_language("en")).grid(row=0, column=0)
ttk.Button(language_frame, text="Español", command=lambda: change_language("es")).grid(row=0, column=1)

# Input channel
input_channel = tk.StringVar(value='mic')
input_channel_label = ttk.Label(main_frame, text="")
input_channel_label.grid(row=1, column=0, pady=10, sticky="w")
input_channel_menu = ttk.OptionMenu(main_frame, input_channel, 'mic', 'mic', 'hiz', 'line', 'mic_hiz', 'mute')
input_channel_menu.grid(row=1, column=1, pady=10, sticky="ew")

# Input volume
input_frame = ttk.LabelFrame(main_frame, text="Input Volume", padding="10")
input_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

input_vol_left = tk.IntVar(value=0)
input_vol_right = tk.IntVar(value=0)

ttk.Label(input_frame, text="Left").grid(row=0, column=0, padx=10)
ttk.Scale(input_frame, from_=0, to_=127, orient='horizontal', variable=input_vol_left, command=lambda v: set_input_volume('l', v)).grid(row=0, column=1)

ttk.Label(input_frame, text="Right").grid(row=1, column=0, padx=10)
ttk.Scale(input_frame, from_=0, to_=127, orient='horizontal', variable=input_vol_right, command=lambda v: set_input_volume('r', v)).grid(row=1, column=1)

# Output volume
output_frame = ttk.LabelFrame(main_frame, text="Output Volume", padding="10")
output_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

output_vol_left = tk.IntVar(value=0)
output_vol_right = tk.IntVar(value=0)

ttk.Label(output_frame, text="Left").grid(row=0, column=0, padx=10)
ttk.Scale(output_frame, from_=0, to_=145, orient='horizontal', variable=output_vol_left, command=lambda v: set_output_volume('L', v)).grid(row=0, column=1)

ttk.Label(output_frame, text="Right").grid(row=1, column=0, padx=10)
ttk.Scale(output_frame, from_=0, to_=145, orient='horizontal', variable=output_vol_right, command=lambda v: set_output_volume('R', v)).grid(row=1, column=1)

# Sync output volumes
sync_var = tk.IntVar(value=0)
sync_check = ttk.Checkbutton(main_frame, text="", variable=sync_var, command=sync_volumes)
sync_check.grid(row=4, column=0, columnspan=2, pady=10)

# Monitoring
monitoring_var = tk.IntVar(value=0)
monitoring_check = ttk.Checkbutton(main_frame, text="", variable=monitoring_var, command=toggle_monitoring)
monitoring_check.grid(row=5, column=0, columnspan=2, pady=10)

# Headphones
headphone_var = tk.IntVar(value=0)
headphone_check = ttk.Checkbutton(main_frame, text="", variable=headphone_var, command=toggle_headphones)
headphone_check.grid(row=6, column=0, columnspan=2, pady=10)

# Load settings on startup
load_current_settings()

# Start the application
window.mainloop()
