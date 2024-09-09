import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import json

CONFIG_FILE = 'config.json'

# Ejecutar comandos
def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        return output
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar comando '{cmd}': {e.output.decode()}")
        return None

# Sincronizar volúmenes de salida
def sync_volumes(val):
    if sync_var.get() == 1:
        output_vol_right.set(val)
        run_command(f"./maya22-control -R {val}")

# Manejar monitoreo activado/desactivado
def toggle_monitoring():
    if monitoring_var.get() == 1:
        run_command("./maya22-control -M")  # Activar monitoreo
    else:
        run_command("./maya22-control -m")  # Desactivar monitoreo
    save_settings()

# Habilitar/Deshabilitar audífonos
def toggle_headphones():
    if headphone_var.get() == 1:
        run_command("./maya22-control -i")  # Habilitar audífonos
    else:
        run_command("./maya22-control -I")  # Deshabilitar audífonos
    save_settings()

# Guardar configuración en un archivo
def save_settings():
    settings = {
        'headphones_enabled': headphone_var.get(),
        'monitoring_enabled': monitoring_var.get(),
        'input_vol_left': input_vol_left.get(),
        'input_vol_right': input_vol_right.get(),
        'output_vol_left': output_vol_left.get(),
        'output_vol_right': output_vol_right.get(),
        'input_channel': input_channel.get()  # Guardar canal de entrada
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f)
    except IOError as e:
        messagebox.showerror("Error", f"Error al guardar la configuración: {e}")

# Cargar configuración desde el archivo
def load_current_settings():
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            
        # Aplicar los valores leídos
        headphone_var.set(settings.get('headphones_enabled', 0))
        monitoring_var.set(settings.get('monitoring_enabled', 0))
        input_vol_left.set(settings.get('input_vol_left', 0))
        input_vol_right.set(settings.get('input_vol_right', 0))
        output_vol_left.set(settings.get('output_vol_left', 0))
        output_vol_right.set(settings.get('output_vol_right', 0))
        input_channel.set(settings.get('input_channel', 'mic'))  # Establecer canal de entrada

    except FileNotFoundError:
        # Si el archivo no existe, inicializar con valores predeterminados
        headphone_var.set(0)
        monitoring_var.set(0)
        input_vol_left.set(0)
        input_vol_right.set(0)
        output_vol_left.set(0)
        output_vol_right.set(0)
        input_channel.set('mic')  # Canal de entrada predeterminado
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error al leer el archivo de configuración.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar la configuración: {e}")

# Crear ventana
window = tk.Tk()
window.title("Control ESI Maya22")

# Centrar ventana
window_width, window_height = 390, 500
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
window.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Crear marco principal
main_frame = ttk.Frame(window, padding="10")
main_frame.grid(row=0, column=0, sticky="nsew")

# Etiqueta para seleccionar canal
ttk.Label(main_frame, text="Seleccionar canal de entrada").grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
input_channel = ttk.Combobox(main_frame, values=['mic', 'hiz', 'line', 'mic_hiz', 'mute'])
input_channel.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
input_channel.bind("<<ComboboxSelected>>", lambda event: [run_command(f"./maya22-control -c {input_channel.get()}"), save_settings()])

# Separador
ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

# Frame de volúmenes de entrada
input_frame = ttk.LabelFrame(main_frame, text="Volumen de Entrada", padding="10")
input_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

# Sliders de volúmenes de entrada
def set_input_volume(side, vol):
    run_command(f"./maya22-control -{side} {vol}")
    save_settings()

ttk.Label(input_frame, text="Izquierda").grid(row=0, column=0, pady=5)
input_vol_left = tk.Scale(input_frame, from_=0, to=127, orient='vertical', command=lambda val: set_input_volume('l', val))
input_vol_left.grid(row=1, column=0, padx=10)

ttk.Label(input_frame, text="Derecha").grid(row=0, column=1, pady=5)
input_vol_right = tk.Scale(input_frame, from_=0, to=127, orient='vertical', command=lambda val: set_input_volume('r', val))
input_vol_right.grid(row=1, column=1, padx=10)

# Frame de volúmenes de salida
output_frame = ttk.LabelFrame(main_frame, text="Volumen de Salida", padding="10")
output_frame.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

# Sliders de volúmenes de salida
def set_output_volume(side, vol):
    run_command(f"./maya22-control -{side} {vol}")
    if side == 'L' and sync_var.get() == 1:
        output_vol_right.set(vol)
        run_command(f"./maya22-control -R {vol}")
    save_settings()

ttk.Label(output_frame, text="Izquierda").grid(row=0, column=0, pady=5)
output_vol_left = tk.Scale(output_frame, from_=0, to=145, orient='vertical', command=lambda val: set_output_volume('L', val))
output_vol_left.grid(row=1, column=0, padx=10)

ttk.Label(output_frame, text="Derecha").grid(row=0, column=1, pady=5)
output_vol_right = tk.Scale(output_frame, from_=0, to=145, orient='vertical', command=lambda val: set_output_volume('R', val))
output_vol_right.grid(row=1, column=1, padx=10)

# Casilla de verificación para sincronizar volúmenes (por defecto activada)
sync_var = tk.IntVar(value=1)
sync_check = ttk.Checkbutton(main_frame, text="Sincronizar volúmenes de salida", variable=sync_var, command=lambda: [sync_volumes(output_vol_left.get()), save_settings()])
sync_check.grid(row=4, column=0, columnspan=2, pady=10)

# Check para activar/desactivar monitoreo
monitoring_var = tk.IntVar(value=0)  # Desactivado por defecto
monitoring_check = ttk.Checkbutton(main_frame, text="Activar monitoreo", variable=monitoring_var, command=toggle_monitoring)
monitoring_check.grid(row=5, column=0, columnspan=2, pady=10)

# Check para habilitar/deshabilitar audífonos
headphone_var = tk.IntVar(value=0)  # Deshabilitado por defecto
headphone_check = ttk.Checkbutton(main_frame, text="Habilitar audífonos", variable=headphone_var, command=toggle_headphones)
headphone_check.grid(row=6, column=0, columnspan=2, pady=10)

# Cargar configuración
load_current_settings()

# Ejecutar ventana principal
window.mainloop()
