#!/bin/bash
# Simple launcher — pastikan venv sudah di-setup via setup.sh atau start.sh
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment belum ada."
    echo "Jalankan: bash setup.sh"
    exit 1
fi

source venv/bin/activate
python main.py
