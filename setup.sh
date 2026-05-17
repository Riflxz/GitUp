#!/bin/bash
set -e

echo "=== GitHub Uploader — Setup ==="

# Cek Python 3.11+
python3 --version | grep -E "3\.(1[1-9]|[2-9][0-9])" || {
  echo "ERROR: Butuh Python 3.11+"
  exit 1
}

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependensi
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Setup selesai! ==="
echo "Jalankan app dengan: source venv/bin/activate && python main.py"
