#!/bin/bash

# Menampilkan pesan bahwa proses dimulai
echo "Memulai proses build AplikasiNPWP..."

# 1. Tentukan path ke virtual environment
VENV_DIR=".env"

# 2. Cek apakah virtual environment ada dan bisa diaktifkan
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Mengaktifkan virtual environment dari '$VENV_DIR'..."
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment '$VENV_DIR/bin/activate' tidak ditemukan."
    echo "Pastikan Anda sudah membuat virtual environment dengan nama '.env'"
    exit 1
fi

# 3. Jalankan perintah PyInstaller
echo "Menjalankan PyInstaller..."
pyinstaller --onefile \
            --windowed \
            --name=AplikasiNPWP \
            --add-data=".myenv:." \
            main.py

# 4. Cek apakah build berhasil
if [ $? -eq 0 ]; then
    echo "==================================================="
    echo "Build SUKSES!"
    echo "Aplikasi Anda ada di folder: dist/AplikasiNPWP"
    echo "==================================================="
else
    echo "==================================================="
    echo "Build GAGAL. Silakan cek pesan error di atas."
    echo "==================================================="
fi

# 5. (Opsional) Nonaktifkan virtual environment setelah selesai
echo "Menonaktifkan virtual environment..."
deactivate