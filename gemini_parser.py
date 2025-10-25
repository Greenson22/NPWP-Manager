# gemini_parser.py
# Mengurus semua logika untuk memanggil Gemini API
# VERSI 2.1 - Memperbaiki penempatan JSON Schema

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from PIL import Image
import json

# --- Variabel Global ---
model = None
api_is_configured = False

# Definisikan skema JSON yang kita inginkan dari AI.
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "nama": {"type": "string"},
        "nik": {"type": "string"},
        "nik_kk": {"type": "string"},
        "no_kk": {"type": "string"},
        "tempat_lahir": {"type": "string"},
        "tanggal_lahir": {"type": "string", "description": "Format YYYY-MM-DD"},
        "alamat": {"type": "string"},
    },
    "required": ["nama", "nik", "nik_kk", "no_kk", "tempat_lahir", "tanggal_lahir", "alamat"]
}


def init_api(api_key: str):
    """
    Menginisialisasi Gemini API dengan key yang diberikan.
    """
    global model, api_is_configured
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            system_instruction = (
                "Anda adalah asisten OCR yang ahli dalam membaca dokumen kependudukan Indonesia (KTP dan KK).\n"
                "Tugas Anda adalah menganalisis gambar, menggabungkan data dari KTP dan KK, dan mengisi skema JSON yang disediakan.\n\n"
                "ATURAN PRIORITAS:\n"
                "1. Gunakan KTP sebagai sumber utama (prioritas 1) untuk: 'nama', 'nik', 'tempat_lahir', 'tanggal_lahir', 'alamat'.\n"
                "2. Gunakan Kartu Keluarga (KK) sebagai sumber utama (prioritas 1) untuk: 'no_kk' dan 'nik_kk' (NIK Kepala Keluarga).\n"
                "3. Jika data di KTP tidak jelas (misal 'alamat' terpotong), Anda boleh menggunakan data dari KK sebagai cadangan (prioritas 2).\n"
                "4. Jika data tidak ditemukan di gambar manapun, kembalikan string kosong \"\"."
            )
            
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro-latest',
                system_instruction=system_instruction
            )
            
            api_is_configured = True
            print("Gemini API (1.5 Pro) berhasil dikonfigurasi.")
        except Exception as e:
            print(f"Konfigurasi Gemini gagal: {e}")
            api_is_configured = False
    else:
        api_is_configured = False
        print("Gemini API Key tidak ditemukan. Fitur AI akan dinonaktifkan.")


def extract_data_from_images(image_paths: list[str]):
    """
    Mengirim BEBERAPA gambar (KTP & KK) ke Gemini API dan meminta
    ekstraksi data yang DIGABUNGKAN dalam format JSON yang dipaksakan.
    """
    
    if not api_is_configured or model is None:
        return False, "Gemini API belum dikonfigurasi.\n\nSilakan masukkan API Key Anda melalui menu 'File' > 'Konfigurasi API Key'."

    try:
        # 1. Muat semua gambar
        loaded_images = []
        for path in image_paths:
            print(f"Memuat gambar: {path}...")
            img = Image.open(path)
            loaded_images.append(img)
            
        if not loaded_images:
            return False, "Tidak ada gambar yang dipilih."

        # --- PERBAIKAN 1 ---
        # Siapkan prompt (HANYA gambar dan teks sederhana)
        # Kita HAPUS JSON_SCHEMA dari sini.
        prompt_parts = loaded_images + [
            "Tolong ekstrak data dari gambar-gambar ini sesuai dengan aturan dan skema JSON yang telah ditentukan."
        ]

        # --- PERBAIKAN 2 ---
        # Konfigurasi untuk JSON Mode
        # Kita TAMBAHKAN 'response_schema' di sini.
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA 
        )
        
        # 4. Panggil API
        response = model.generate_content(
            prompt_parts,
            generation_config=generation_config
        )
        
        # 5. Parsing Respon
        print(f"Respon JSON API: {response.text}")
        data_dict = json.loads(response.text)
        
        return True, data_dict

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        # Tangani error spesifik jika ada
        if "response" in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Detail Error: {response.prompt_feedback}")
        return False, f"Terjadi kesalahan saat memproses gambar: {e}"