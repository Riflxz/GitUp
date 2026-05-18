#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

APP_NAME="GitForge"

# ── Help ──────────────────────────────────────────────────────────
show_help() {
    echo "Usage: bash run.sh <command>"
    echo ""
    echo "Commands:"
    echo "  start       Jalankan aplikasi (auto-setup jika venv belum ada)"
    echo "  setup       Buat virtual environment dan install dependensi"
    echo "  check       Periksa dependencies (Python, tkinter, libmpv)"
    echo "  help        Tampilkan bantuan ini"
    echo ""
    echo "Contoh:"
    echo "  bash run.sh          # sama dengan 'start'"
    echo "  bash run.sh setup"
    echo "  bash run.sh check"
}

# ── Deteksi distro ────────────────────────────────────────────────
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

# ── Cari Python 3.11+ ─────────────────────────────────────────────
find_python() {
    for cmd in python3.14 python3.13 python3.12 python3.11 python3; do
        if command -v "$cmd" >/dev/null 2>&1; then
            ver=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# ── Setup ──────────────────────────────────────────────────────────
cmd_setup() {
    PYTHON=$(find_python) || {
        DISTRO=$(detect_distro)
        echo "ERROR: Python 3.11+ tidak ditemukan."
        case "$DISTRO" in
            arch|manjaro|endeavouros)     echo "  sudo pacman -S python python-pip git tk" ;;
            ubuntu|debian|pop|linuxmint)  echo "  sudo apt install python3 python3-pip python3-venv git python3-tk" ;;
            fedora|rhel|centos)           echo "  sudo dnf install python3 python3-pip git python3-tkinter" ;;
            opensuse*|suse)               echo "  sudo zypper install python3 python3-pip git python3-tk" ;;
            *)                            echo "  Install Python 3.11+ melalui package manager Anda." ;;
        esac
        exit 1
    }

    if [ -d "venv" ]; then
        echo "venv sudah ada, memperbarui..."
    else
        echo "Membuat virtual environment..."
        "$PYTHON" -m venv venv
    fi

    source venv/bin/activate
    pip install --upgrade pip -q

    if pip install -r requirements.txt -q; then
        echo "Setup selesai."
    else
        echo "Mencoba dengan --break-system-packages..."
        pip install --break-system-packages -r requirements.txt -q
        echo "Setup selesai."
    fi
}

# ── Check ──────────────────────────────────────────────────────────
cmd_check() {
    echo "=== $APP_NAME — System Check ==="

    PYTHON=$(find_python) || { echo "Python 3.11+: TIDAK"; exit 1; }
    echo "Python: $("$PYTHON" --version 2>&1)"

    echo "Git:    $(git --version 2>&1 || echo 'TIDAK')"

    TK_CHECK=$("$PYTHON" -c "import tkinter" 2>&1 || echo "missing")
    if [ "$TK_CHECK" = "missing" ]; then
        echo "tkinter: TIDAK (file dialog mungkin error)"
        DISTRO=$(detect_distro)
        case "$DISTRO" in
            arch|manjaro|endeavouros)     echo "  Install: sudo pacman -S tk" ;;
            ubuntu|debian|pop|linuxmint)  echo "  Install: sudo apt install python3-tk" ;;
            fedora|rhel|centos)           echo "  Install: sudo dnf install python3-tkinter" ;;
            opensuse*|suse)               echo "  Install: sudo zypper install python3-tk" ;;
        esac
    else
        echo "tkinter: OK"
    fi

    if ldconfig -p 2>/dev/null | grep -q "libmpv\.so\.1"; then
        echo "libmpv:  OK"
    else
        _MPV_LIB=$(find /usr/lib /usr/lib64 /usr/local/lib -name "libmpv.so.*" -type f 2>/dev/null | head -1)
        if [ -z "$_MPV_LIB" ] && command -v pacman >/dev/null 2>&1; then
            _MPV_LIB=$(pacman -Ql mpv 2>/dev/null | grep "libmpv\.so\." | awk '{print $2}' | head -1)
        fi
        if [ -n "$_MPV_LIB" ]; then
            echo "libmpv:  $_MPV_LIB (symlink akan dibuat saat start)"
        else
            echo "libmpv:  TIDAK"
            DISTRO=$(detect_distro)
            case "$DISTRO" in
                arch|manjaro|endeavouros)     echo "  Install: sudo pacman -S mpv" ;;
                ubuntu|debian|pop|linuxmint)  echo "  Install: sudo apt install libmpv-dev" ;;
                fedora|rhel|centos)           echo "  Install: sudo dnf install mpv-libs" ;;
            esac
        fi
    fi
}

# ── Start ──────────────────────────────────────────────────────────
cmd_start() {
    if [ ! -d "venv" ]; then
        echo "venv belum ada, menjalankan setup dulu..."
        cmd_setup
    fi

    source venv/bin/activate

    # libmpv symlink
    _LOCAL_LIBS="$APP_DIR/.local-libs"
    mkdir -p "$_LOCAL_LIBS"
    if ! ldconfig -p 2>/dev/null | grep -q "libmpv\.so\.1"; then
        _MPV_LIB=$(find /usr/lib /usr/lib64 /usr/local/lib -name "libmpv.so.*" -type f 2>/dev/null | head -1)
        if [ -z "$_MPV_LIB" ] && command -v pacman >/dev/null 2>&1; then
            _MPV_LIB=$(pacman -Ql mpv 2>/dev/null | grep "libmpv\.so\." | awk '{print $2}' | head -1)
        fi
        if [ -n "$_MPV_LIB" ]; then
            ln -sf "$_MPV_LIB" "$_LOCAL_LIBS/libmpv.so.1"
        fi
    fi
    export LD_LIBRARY_PATH="$_LOCAL_LIBS:$LD_LIBRARY_PATH"

    echo "Menjalankan $APP_NAME..."
    python3 main.py
}

# ── Main ───────────────────────────────────────────────────────────
case "${1:-start}" in
    start)
        cmd_start
        ;;
    setup)
        cmd_setup
        ;;
    check)
        cmd_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Perintah tidak dikenal: $1"
        echo "Gunakan: bash run.sh help"
        exit 1
        ;;
esac
