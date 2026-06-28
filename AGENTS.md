# AGENTS.md — ESI Maya22 Linux GUI

## Descripción del Proyecto
Interfaz gráfica para controlar la interfaz de audio ESI Maya22 USB en Linux mediante el binario `maya22-control`.

## Archivos Clave
- `maya22-gui.py` — GUI principal (CustomTkinter)
- `config.json` — Configuración persistente
- `maya22-control` — Binario que envía comandos al hardware
- `requerimientos.txt` — Dependencias del sistema
- `images/` — Screenshots e iconos
- `build-deb.sh` — Script para generar .deb
- `debian/` — Estructura para empaquetado Debian

## Código Fuente Oficial
- Repo: `/home/adrian/Proyectos/esi-maya22-linux/`
- Fuente: `maya22-control.c` (C, usa hidapi)
- Compilar: `make` (necesita `libhidapi-dev`)
- El binario oficial compilado tiene el help text correcto (`-i` = Enable all outputs, `-I` = Disable all outputs)

## Binario `maya22-control` — Flags
| Flag | Descripción | Código HID |
|------|-------------|------------|
| `-e` | Enumerar dispositivos | — |
| `-i` | **Habilitar** todas las salidas | `send(0x1a, 0x00)` |
| `-I` | **Deshabilitar** todas las salidas | `send(0x1a, 0x01)` |
| `-d` | Valores por defecto (enable outs, vol 86/86/145/145, ch mic_hiz) | múltiple |
| `-c <name>` | Canal de entrada: mic, hiz, line, mic_hiz, mute | `send(0x2a, val)` |
| `-M` | Input monitoring ON | `send(0x2c, 0x05)` |
| `-m` | Input monitoring OFF | `send(0x2c, 0x01)` |
| `-l <0-127>` | Volumen entrada izquierda | `send(0x1c, val+104)` |
| `-r <0-127>` | Volumen entrada derecha | `send(0x1e, val+104)` |
| `-L <0-145>` | Volumen salida izquierda | `send(0x07, val+110)` |
| `-R <0-145>` | Volumen salida derecha | `send(0x09, val+110)` |

## Estado Actual
- GUI funcional con CustomTkinter, dark/light mode automático
- Manejo de errores básico (try/except en comandos y config)
- Icono SVG + PNGs multi-resolución
- Empaquetado .deb funcional con `build-deb.sh`

## Plan de Mejora
1. Migrar de tkinter/ttk a **CustomTkinter** (apariencia moderna, soporte dark/light mode)
2. Unificar en un solo archivo (`maya22-gui.py`)
3. Arreglar layout (grid bien estructurado, sin overlaps)
4. Agregar manejo de errores robusto
5. Mejorar UX (tooltips, feedback visual)
6. Soporte para tema oscuro/claro
7. Eliminar `control.py` (obsoleto)

## Dependencias
```
pip install customtkinter
```

## Comandos Útiles
```bash
python maya22-gui.py              # Ejecutar GUI
./maya22-control -d               # Ver estado del dispositivo
./maya22-control -c line -l 100   # Ejemplo de comando directo
```
