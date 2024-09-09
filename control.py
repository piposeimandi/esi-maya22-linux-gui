import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# Ejecutar comandos
def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True).decode()
        return output
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar comando: {e}")
        return None

# Sincronizar volúmenes de salida
def sync_volumes(val):
    if sync_var.get() == 1:
        output_vol_right.set(val)
        run_command(f"maya22-control -R {val}")

# Manejar monitoreo activado/desactivado
def toggle_monitoring():
    if monitoring_var.get() == 1:
        run_command("maya22-control -M")  # Activar monitoreo
    else:
        run_command("maya22-control -m")  # Desactivar monitoreo

# Habilitar audífonos
def enable_headphones():
    run_command("maya22-control -i")  # Habilitar audífonos

# Obtener los valores actuales del dispositivo
def load_current_settings():
    output = run_command("maya22-control -d")
    if output:
        # Parsear los datos obtenidos
        if "Enable headphone" in output:
            headphone_button.config(state="disabled")  # Audífonos habilitados
        if "Set monitor: enable" in output:
            monitoring_var.set(1)  # Monitoreo activado
        else:
            monitoring_var.set(0)  # Monitoreo desactivado
        if "Set input left volume" in output:
            left_input_vol = int(output.split("Set input left volume: ")[1].split("\n")[0])
            input_vol_left.set(left_input_vol)
        if "Set input right volume" in output:
            right_input_vol = int(output.split("Set input right volume: ")[1].split("\n")[0])
            input_vol_right.set(right_input_vol)
        if "Set output left volume" in output:
            left_output_vol = int(output.split("Set output left volume: ")[1].split("\n")[0])
            output_vol_left.set(left_output_vol)
        if "Set output right volume" in output:
            right_output_vol = int(output.split("Set output right volume: ")[1].split("\n")[0])
            output_vol_right.set(right_output_vol)

# Crear ventana
window = tk.Tk()
window.title("Control ESI Maya22")

# Centrar ventana
window_width, window_height = 400, 500
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
input_channel.bind("<<ComboboxSelected>>", lambda event: run_command(f"maya22-control -c {input_channel.get()}"))

# Separador
ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

# Frame de volúmenes de entrada
input_frame = ttk.LabelFrame(main_frame, text="Volumen de Entrada", padding="10")
input_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

# Sliders de volúmenes de entrada
def set_input_volume(side, vol):
    run_command(f"maya22-control -{side} {vol}")

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
    run_command(f"maya22-control -{side} {vol}")
    if side == 'L' and sync_var.get() == 1:
        output_vol_right.set(vol)
        run_command(f"maya22-control -R {vol}")

ttk.Label(output_frame, text="Izquierda").grid(row=0, column=0, pady=5)
output_vol_left = tk.Scale(output_frame, from_=0, to=145, orient='vertical', command=lambda val: set_output_volume('L', val))
output_vol_left.grid(row=1, column=0, padx=10)

ttk.Label(output_frame, text="Derecha").grid(row=0, column=1, pady=5)
output_vol_right = tk.Scale(output_frame, from_=0, to=145, orient='vertical', command=lambda val: set_output_volume('R', val))
output_vol_right.grid(row=1, column=1, padx=10)

# Casilla de verificación para sincronizar volúmenes (por defecto activada)
sync_var = tk.IntVar(value=1)
sync_check = ttk.Checkbutton(main_frame, text="Sincronizar volúmenes de salida", variable=sync_var)
sync_check.grid(row=4, column=0, columnspan=2, pady=10)

# Check para activar/desactivar monitoreo
monitoring_var = tk.IntVar(value=0)  # Desactivado por defecto
monitoring_check = ttk.Checkbutton(main_frame, text="Activar monitoreo", variable=monitoring_var, command=toggle_monitoring)
monitoring_check.grid(row=5, column=0, columnspan=2, pady=10)

# Botón para habilitar audífonos
headphone_button = ttk.Button(main_frame, text="Habilitar audífonos", command=enable_headphones)
headphone_button.grid(row=6, column=0, columnspan=2, pady=10)

# Cargar valores actuales del dispositivo al inicio
load_current_settings()

# Expandir para adaptarse a la ventana
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Ejecutar ventana
window.mainloop()
