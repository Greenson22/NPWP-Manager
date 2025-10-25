#!/bin/bash
#
# Script untuk mengompilasi aplikasi NPWP menggunakan Nuitka.
#
# CARA MENGGUNAKAN:
# 1. Simpan file ini di folder root proyek Anda (di luar folder 'code').
# 2. Beri izin eksekusi: chmod +x build.sh
# 3. Jalankan script:    ./build.sh
#

# --- Konfigurasi ---
# (Ubah ini jika nama folder virtual environment Anda berbeda)
VENV_FOLDER="venv"

# Menentukan file Python utama
MAIN_SCRIPT="code/main.py"

# --------------------

# Hentikan script jika ada perintah yang gagal
set -e

echo "--- Memulai proses build Nuitka ---"

# 1. Cek dan Aktifkan Virtual Environment
echo "Mencari virtual environment di: $VENV_FOLDER/"
if [ ! -d "$VENV_FOLDER" ]; then
    echo "Error: Folder virtual environment '$VENV_FOLDER' tidak ditemukan."
    echo "Harap buat dulu (python3 -m venv $VENV_FOLDER) atau perbaiki nama VENV_FOLDER di script ini."
    exit 1
fi

echo "Mengaktifkan virtual environment..."
source "$VENV_FOLDER/bin/activate"

# 2. Menjalankan Nuitka
echo "Menjalankan Nuitka untuk $MAIN_SCRIPT..."
echo "(Proses ini mungkin memakan waktu beberapa menit)"

nuitka --onefile \
       --enable-plugin=pyqt6 \
       --output-dir=dist \
       --remove-output \
       $MAIN_SCRIPT

echo ""
echo "--- Build Selesai! ---"
echo "File eksekutabel Anda telah dibuat di dalam folder 'dist/'."
echo "CATATAN: Jangan lupa untuk menyertakan file '.myenv' di samping file eksekutabel agar API Key bisa terbaca."

# Deaktivasi (opsional, karena script akan berakhir)
deactivate