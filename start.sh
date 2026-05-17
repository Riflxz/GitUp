#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

echo "=== GitHub Uploader ==="

# ── Deteksi distro ───────────────────────────────────────────────
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command -v lsb_release >/dev/null 2>&1; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)

# ── Cari Python 3.11+ ────────────────────────────────────────────
PYTHON=""
for cmd in python3.14 python3.13 python3.12 python3.11 python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
        ver=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.11+ tidak ditemukan."
    case "$DISTRO" in
        arch|manjaro|endeavouros)     echo "    sudo pacman -S python python-pip git tk" ;;
        ubuntu|debian|pop|linuxmint)  echo "    sudo apt install python3 python3-pip python3-venv git python3-tk" ;;
        fedora|rhel|centos)           echo "    sudo dnf install python3 python3-pip git python3-tkinter" ;;
        opensuse*|suse)               echo "    sudo zypper install python3 python3-pip git python3-tk" ;;
        *)                            echo "    Install Python 3.11+ melalui package manager Anda." ;;
    esac
    exit 1
fi

# ── Setup venv ────────────────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    "$PYTHON" -m venv venv
    source venv/bin/activate
    echo "Menginstall dependensi..."
    pip install --upgrade pip -q
    if pip install -r requirements.txt -q; then
        echo "Setup selesai."
    else
        echo "Mencoba dengan --break-system-packages..."
        pip install --break-system-packages -r requirements.txt -q
        echo "Setup selesai."
    fi
else
    source venv/bin/activate
fi

# ── Cek tkinter ───────────────────────────────────────────────────
TK_CHECK=$("$PYTHON" -c "import tkinter" 2>&1 || echo "missing")
if [ "$TK_CHECK" = "missing" ]; then
    echo "Peringatan: tkinter tidak tersedia. File dialog mungkin tidak berfungsi."
    case "$DISTRO" in
        arch|manjaro|endeavouros)     echo "  Install: sudo pacman -S tk" ;;
        ubuntu|debian|pop|linuxmint)  echo "  Install: sudo apt install python3-tk" ;;
        fedora|rhel|centos)           echo "  Install: sudo dnf install python3-tkinter" ;;
        opensuse*|suse)               echo "  Install: sudo zypper install python3-tk" ;;
    esac
fi

# ── Cek libmpv (dibutuhkan Flet) ──────────────────────────────────
_LOCAL_LIBS="$APP_DIR/.local-libs"
mkdir -p "$_LOCAL_LIBS"

if ! ldconfig -p 2>/dev/null | grep -q "libmpv\.so\.1"; then
    _MPV_LIB=$(find /usr/lib /usr/lib64 /usr/local/lib -name "libmpv.so.*" -type f 2>/dev/null | head -1)
    if [ -z "$_MPV_LIB" ] && command -v pacman >/dev/null 2>&1; then
        _MPV_LIB=$(pacman -Ql mpv 2>/dev/null | grep "libmpv\.so\." | awk '{print $2}' | head -1)
    fi
    if [ -n "$_MPV_LIB" ]; then
        ln -sf "$_MPV_LIB" "$_LOCAL_LIBS/libmpv.so.1"
        echo "Membuat symlink libmpv: $_MPV_LIB -> libmpv.so.1"
    else
        echo "Peringatan: libmpv tidak ditemukan."
        case "$DISTRO" in
            arch|manjaro|endeavouros)     echo "  Install: sudo pacman -S mpv" ;;
            ubuntu|debian|pop|linuxmint)  echo "  Install: sudo apt install libmpv-dev" ;;
            fedora|rhel|centos)           echo "  Install: sudo dnf install mpv-libs" ;;
        esac
    fi
fi

export LD_LIBRARY_PATH="$_LOCAL_LIBS:$LD_LIBRARY_PATH"

# ── Jalankan ──────────────────────────────────────────────────────
echo "Menjalankan aplikasi..."
"$PYTHON" main.py
