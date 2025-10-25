# gemini_parser.py
# Mengurus semua logika untuk memanggil Gemini API

import google.generativeai as genai
from PIL import Image
import json

# --- Variabel Global ---
# Kita set ke None. Ini akan diisi oleh main.py saat startup.
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

def extract_data_from_image(image_path: str):
    """
    Mengirim gambar ke Gemini API dan meminta ekstraksi data
    dalam format JSON.
    """
    
    # --- Pemeriksaan BARU ---
    # Cek apakah init_api() sudah berhasil dipanggil
    if not api_is_configured or model is None:
        return False, "Gemini API belum dikonfigurasi.\n\nSilakan masukkan API Key Anda melalui menu 'File' > 'Konfigurasi API Key'."

    # --- Logika yang ada (sedikit diubah) ---
    try:
        print(f"Memproses gambar: {image_path}...")
        img = Image.open(image_path)
        
        prompt_parts = [
            img,
            "\n\nAnalisis gambar (yang mungkin berupa KTP atau Kartu Keluarga Indonesia) dan ekstrak data berikut.\n"
            "Kembalikan HANYA string JSON yang valid.\n"
            "Kunci JSON yang harus digunakan (gunakan string kosong \"\" jika data tidak ditemukan):\n"
            "- 'nama' (Nama Lengkap)\n"
            "- 'nik' (NIK)\n"
            "- 'nik_kk' (Jika ini KK, ambil NIK Kepala Keluarga)\n"
            "- 'no_kk' (Nomor Kartu Keluarga)\n"
            "- 'tempat_lahir' (Tempat Lahir)\n"
            "- 'tanggal_lahir' (Tanggal Lahir, format YYYY-MM-DD)\n"
            "- 'alamat' (Alamat lengkap)\n"
            "\nContoh JSON: {\"nama\": \"BUDI SANTOSO\", \"nik\": \"3170123456780001\", ...}\n"
            "JSON:\n"
        ]

        # Panggil API
        response = model.generate_content(prompt_parts)
        
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        print(f"Respon mentah API: {raw_text}")
        
        data_dict = json.loads(raw_text)
        
        return True, data_dict

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return False, f"Terjadi kesalahan: {e}"