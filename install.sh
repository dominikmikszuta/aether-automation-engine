#!/bin/bash
set -e
if command -v pkg >/dev/null 2>&1; then
  pkg update -y >/dev/null 2>&1 || true
  pkg install -y python python-pip clang make pkg-config libjpeg-turbo zlib freetype python-pillow >/dev/null 2>&1 || true
fi
pip install --upgrade pip >/dev/null 2>&1 || true
pip install fpdf2 Pillow >/dev/null 2>&1
python -c "import fpdf" && echo "OK"
