# gemini_parser.py
# Mengurus semua logika untuk memanggil Gemini API

import google.generativeai as genai
from PIL import Image
import json

# --- Variabel Global ---
model = None
api_is_configured = False

def init_api(api_key: str):
    """
    Menginisialisasi Gemini API dengan key yang diberikan.
    Dipanggil oleh main.py saat aplikasi dimulai.
    """
    global model, api_is_configured
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            api_is_configured = True
            print("Gemini API berhasil dikonfigurasi.")
        except Exception as e:
            print(f"Konfigurasi Gemini gagal: {e}")
            api_is_configured = False
    else:
        api_is_configured = False
        print("Gemini API Key tidak ditemukan. Fitur AI akan dinonaktifkan.")

# --- FUNGSI DIPERBARUI ---
def extract_data_from_images(image_paths: list[str]):
    """
    Mengirim BEBERAPA gambar (KTP & KK) ke Gemini API dan meminta
    ekstraksi data yang DIGABUNGKAN dalam format JSON.
    """
    
    if not api_is_configured or model is None:
        return False, "Gemini API belum dikonfigurasi.\n\nSilakan masukkan API Key Anda melalui menu 'File' > 'Konfigurasi API Key'."

    try:
        # 1. Muat semua gambar yang dipilih
        loaded_images = []
        for path in image_paths:
            print(f"Memuat gambar: {path}...")
            img = Image.open(path)
            loaded_images.append(img)
            
        if not loaded_images:
            return False, "Tidak ada gambar yang dipilih."

        # 2. Buat Prompt Multi-Gambar yang Cerdas
        prompt_text = (
            "\n\nAnalisis gambar-gambar berikut (yang kemungkinan adalah KTP dan Kartu Keluarga Indonesia).\n"
            "Tugas Anda adalah MENGGABUNGKAN data dari semua gambar untuk mengisi SATU objek JSON.\n\n"
            "ATURAN PRIORITAS:\n"
            "1. Gunakan KTP sebagai sumber utama (prioritas 1) untuk: 'nama', 'nik', 'tempat_lahir', 'tanggal_lahir', 'alamat'.\n"
            "2. Gunakan Kartu Keluarga (KK) sebagai sumber utama (prioritas 1) untuk: 'no_kk' dan 'nik_kk' (NIK Kepala Keluarga).\n"
            "3. Jika data di KTP tidak jelas (misal 'alamat' terpotong), Anda boleh menggunakan data dari KK sebagai cadangan (prioritas 2).\n\n"
            "Kembalikan HANYA string JSON yang valid.\n"
            "Kunci JSON yang harus digunakan (gunakan string kosong \"\" jika data tidak ditemukan):\n"
            "- 'nama' (Nama Lengkap, prioritas KTP)\n"
            "- 'nik' (NIK, prioritas KTP)\n"
            "- 'nik_kk' (NIK Kepala Keluarga, prioritas KK)\n"
            "- 'no_kk' (Nomor Kartu Keluarga, prioritas KK)\n"
            "- 'tempat_lahir' (Tempat Lahir, prioritas KTP)\n"
            "- 'tanggal_lahir' (Tanggal Lahir, format YYYY-MM-DD, prioritas KTP)\n"
            "- 'alamat' (Alamat lengkap, prioritas KTP)\n"
            "\nContoh JSON: {\"nama\": \"BUDI SANTOSO\", \"nik\": \"3170123456780001\", ...}\n"
            "JSON:\n"
        )
        
        # 3. Gabungkan gambar dan teks prompt
        # [gambar1, gambar2, ..., teks_prompt]
        prompt_parts = loaded_images + [prompt_text]

        # 4. Panggil API
        response = model.generate_content(prompt_parts)
        
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        print(f"Respon mentah API (multi-gambar): {raw_text}")
        
        data_dict = json.loads(raw_text)
        
        return True, data_dict

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return False, f"Terjadi kesalahan: {e}"