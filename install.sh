#!/usr/bin/env bash
#
# install.sh — Instalador para la GUI de control de la ESI MAYA22 USB en Fedora
#
# Hace todo de forma automática e idempotente (se puede correr varias veces):
#   1. Verifica distro + sudo
#   2. Instala dependencias de sistema (dnf)
#   3. Obtiene/actualiza el repo de la GUI
#   4. Crea el venv e instala customtkinter + Pillow
#   5. Aplica el fix del icono (idempotente)
#   6. Compila maya22-control
#   7. Crea la regla udev para acceso al dispositivo (sin root)
#   8. Crea el launcher .desktop de KDE + refresca el menú
#   9. Instala acceso directo en ~/.local/bin
#
# Uso:
#   ./install.sh            # setup completo
#   ./install.sh --no-dnf   # saltea la instalación de paquetes de sistema
#
set -euo pipefail

# ---------------------------------------------------------------- helpers
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ------------------------------------------------------- constantes & config
REPO_URL="https://github.com/piposeimandi/esi-maya22-linux-gui.git"
DEFAULT_DIR="$HOME/esi-maya22-linux-gui"
REPO_DIR="${MAYA22_DIR:-$DEFAULT_DIR}"
VENV="$REPO_DIR/.venv"
BIN_TARGET="$HOME/.local/bin/maya22-gui"
DESKTOP_FILE="$HOME/.local/share/applications/maya22-control.desktop"
ICON_SRC="$REPO_DIR/images/maya22-icon.svg"

# IDs USB del dispositivo ESI MAYA22
USB_VENDOR="2573"
USB_PRODUCT="0017"

DO_DNF=1
[[ "${1:-}" == "--no-dnf" ]] && DO_DNF=0

# ------------------------------------------------------- 0. chequeos previos
command -v sudo >/dev/null 2>&1 || die "Se necesita 'sudo' para instalar los paquetes de sistema."
[[ "$(id -u)" -eq 0 ]] && warn "Lo estás corriendo como root. Mejor ró se como tu usuario normal (sudo pedirá la clave)."
command -v git  >/dev/null 2>&1 || die "Se necesita 'git'. Instala: sudo dnf install git"

# Verificar distro
if [[ -r /etc/os-release ]]; then
    . /etc/os-release
    if [[ "$ID" != "fedora" ]]; then
        die "Este instalador está pensado para Fedora (detectado: '$ID'). Abortando por seguridad."
    fi
else
    die "No se pudo detectar la distribución."
fi
info "Fedora detectado: ${PRETTY_NAME:-$VERSION_ID:-Fedora}"

# ------------------------------------------------------- 1. deps de sistema
if [[ "$DO_DNF" -eq 1 ]]; then
    info "Instalando dependencias de sistema (dnf)..."
    sudo dnf install -y \
        git \
        gcc make \
        hidapi-devel \
        python3-tkinter \
        python3-pillow \
        python3-pillow-tk 2>/dev/null || {
        # pillow-tk puede no existir en algunas versiones; no es bloqueante
        sudo dnf install -y git gcc make hidapi-devel python3-tkinter python3-pillow
    }
    info "Dependencias de sistema instaladas."
else
    warn "--no-dnf: salteando instalación de paquetes de sistema."
fi

# ------------------------------------------------------- 2. obtener el repo
if [[ ! -d "$REPO_DIR/.git" ]]; then
    info "Clonando el repositorio de la GUI en $REPO_DIR ..."
    git clone "$REPO_URL" "$REPO_DIR"
else
    info "Repo ya presente en $REPO_DIR; verificando actualizaciones..."
    git -C "$REPO_DIR" pull --ff-only 2>/dev/null || warn "No se pudo actualizar el repo (cambios locales). Continuando con el estado actual."
fi

# ------------------------------------------------------- 3. venv + deps python
if [[ ! -x "$VENV/bin/python" ]]; then
    info "Creando entorno virtual en $VENV ..."
    python3 -m venv "$VENV"
fi
info "Instalando dependencias Python (customtkinter, Pillow)..."
"$VENV/bin/pip" install --upgrade pip >/dev/null
"$VENV/bin/pip" install customtkinter Pillow

# ------------------------------------------------------- 4. fix del icono
# La GUI pasa un CTkImage a wm_iconphoto(), lo que rompe en customtkinter 6 + Tk 9.
# Este fix reemplaza el bloque original de 3 lineas por el bloque con try/except.
# Es IDEMPOTENTE y de complejidad O(n) (sin regex/backtracking): tras aplicarlo,
# el patron original desaparece y las corridas siguientes no cambian nada.
GUI_PY="$REPO_DIR/maya22-gui.py"
RESULT="$(python3 - "$GUI_PY" <<'PY'
import sys
ORIGINAL = (
    "        if os.path.exists(icon_path):\n"
    "            icon_img = Image.open(icon_path)\n"
    "            self.iconphoto(True, ctk.CTkImage(icon_img, size=(32, 32)))\n"
)
FIXED = (
    "        if os.path.exists(icon_path):\n"
    "            try:\n"
    "                icon_img = Image.open(icon_path)\n"
    "                icon_img.thumbnail((32, 32))\n"
    "                self.iconphoto(True, ctk.CTkImage(icon_img, size=(32, 32)))\n"
    "            except Exception:\n"
    "                pass\n"
)
with open(sys.argv[1]) as f:
    src = f.read()
if ORIGINAL in src:
    open(sys.argv[1], "w").write(src.replace(ORIGINAL, FIXED, 1))
    print("FIX_APPLIED")
elif "icon_img.thumbnail((32, 32))" in src and "except Exception:" in src:
    print("ALREADY_FIXED")
else:
    print("PATTERN_MISS")
PY
)"
case "$RESULT" in
    FIX_APPLIED)  info "Fix del icono aplicado (compatibilidad customtkinter 6 / Tk 9)." ;;
    ALREADY_FIXED) info "Fix del icono ya aplicado; no se modifica nada." ;;
    *) warn "No se detectó el patrón del icono con certeza ($RESULT). Continuando." ;;
esac

# Asegurar ejecutable
chmod +x "$REPO_DIR/maya22-gui.py" "$REPO_DIR/maya22-control" 2>/dev/null || true

# ------------------------------------------------------- 5. verificar binario
# El repo de la GUI incluye 'maya22-control' ya compilado (ELF x86-64 GNU/Linux).
# Se verifica que exista y sea ejecutable en la arquitectura actual.
CONTROL_BIN="$REPO_DIR/maya22-control"
if [[ ! -x "$CONTROL_BIN" ]]; then
    die "No se encontró '$CONTROL_BIN'. ¿El clon quedó incompleto?"
fi
info "Binario maya22-control presente:"
file "$CONTROL_BIN" | sed 's/^/  /'

# ------------------------------------------------------- 6. regla udev
RULES_FILE="/etc/udev/rules.d/50-esi-maya22.rules"
# En Fedora no existe el grupo 'plugdev'. Usamos 'wheel' si el usuario está en él,
# de lo contrario damos permisos generales (0666) para equipos de escritorio.
RULES_GROUP="wheel"
if id -nG "$USER" | tr ' ' '\n' | grep -qx wheel; then
    RULES_MODE="0660"
else
    RULES_MODE="0666"
    warn "Tu usuario no está en el grupo 'wheel'; usando MODE=0666 (acceso general)."
fi

RULES_BODY="KERNEL==\"hidraw*\", SUBSYSTEM==\"hidraw\", ATTRS{idVendor}==\"$USB_VENDOR\", ATTRS{idProduct}==\"$USB_PRODUCT\", GROUP=\"$RULES_GROUP\", MODE=\"$RULES_MODE\""

if [[ -f "$RULES_FILE" ]] && grep -qF "idVendor==\"$USB_VENDOR\"" "$RULES_FILE"; then
    info "Regla udev ya presente en $RULES_FILE"
else
    info "Creando regla udev en $RULES_FILE"
    echo "$RULES_BODY" | sudo tee "$RULES_FILE" >/dev/null
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    warn "IMPORTANTE: desconectá y volvé a conectar la placa USB para aplicar los nuevos permisos."
fi

# ------------------------------------------------------- 7. launcher .desktop KDE
mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=MAYA22 USB Control
Comment=Control panel for the ESI MAYA22 USB audio interface
Exec=$VENV/bin/python $REPO_DIR/maya22-gui.py
Icon=$ICON_SRC
Terminal=false
Categories=AudioVideo;Audio;Mixer;
StartupNotify=false
EOF
info "Launcher de escritorio: $DESKTOP_FILE"

# refrescar menú de KDE / caché de aplicaciones
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 >/dev/null 2>&1 || true
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true

# ------------------------------------------------------- 8. acceso directo en ~/.local/bin
mkdir -p "$HOME/.local/bin"
cat > "$BIN_TARGET" <<EOF
#!/bin/bash
exec "$VENV/bin/python" "$REPO_DIR/maya22-gui.py" "\$@"
EOF
chmod +x "$BIN_TARGET"
info "Acceso directo: $BIN_TARGET"

# ------------------------------------------------------- resumen final
echo
echo "============================================================"
echo "  Instalación completada."
echo "============================================================"
echo "  Para abrir la GUI:"
echo "    1) Menú de KDE -> busca 'MAYA22 USB Control'"
echo "    2) o en terminal:  maya22-gui"
echo
echo "  Si es la primera vez (o reconectaste la placa):"
echo "     - Verificá permisos con:  $CONTROL_BIN -e"
echo "     - Activá auriculares:     $CONTROL_BIN -i"
echo "     - Subí volumen:           $CONTROL_BIN -L 120 -R 120"
echo "============================================================"
