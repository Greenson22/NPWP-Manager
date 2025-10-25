# gemini_parser.py
# Mengurus semua logika untuk memanggil Gemini API
# VERSI 3.2 - Revert ke 'GenerativeModel' (V2.1) tapi tetap
#             mendukung pemilihan model (V3.1).

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from PIL import Image
import json

# --- Variabel Global ---
model = None # Kita kembali menggunakan 'model'
api_is_configured = False
current_model_name = "" # Variabel ini tetap ada

# Skema JSON (tidak berubah)
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

# Instruksi Sistem (tidak berubah)
SYSTEM_INSTRUCTION = (
    "Anda adalah asisten OCR yang ahli dalam membaca dokumen kependudukan Indonesia (KTP dan KK).\n"
    "Tugas Anda adalah menganalisis gambar, menggabungkan data dari KTP dan KK, dan mengisi skema JSON yang disediakan.\n\n"
    "ATURAN PRIORITAS:\n"
    "1. Gunakan KTP sebagai sumber utama (prioritas 1) untuk: 'nama', 'nik', 'tempat_lahir', 'tanggal_lahir', 'alamat'.\n"
    "2. Gunakan Kartu Keluarga (KK) sebagai sumber utama (prioritas 1) untuk: 'no_kk' dan 'nik_kk' (NIK Kepala Keluarga).\n"
    "3. Jika data di KTP tidak jelas (misal 'alamat' terpotong), Anda boleh menggunakan data dari KK sebagai cadangan (prioritas 2).\n"
    "4. Jika data tidak ditemukan di gambar manapun, kembalikan string kosong \"\"."
)

# --- FUNGSI DIPERBARUI ---
def init_api(api_key: str):
    """
    Menginisialisasi Gemini API (SDK lama) dengan key.
    """
    global api_is_configured
    
    if api_key:
        try:
            # Ini adalah syntax SDK yang Anda miliki
            genai.configure(api_key=api_key)
            api_is_configured = True
            print("Gemini API (google.generativeai) berhasil dikonfigurasi.")
        except Exception as e:
            print(f"Konfigurasi Gemini gagal: {e}")
            api_is_configured = False
    else:
        api_is_configured = False
        print("Gemini API Key tidak ditemukan. Fitur AI akan dinonaktifkan.")

# --- FUNGSI DIPERBARUI ---
def set_model(model_name: str):
    """
    Dipanggil oleh main.py untuk membuat instance model.
    """
    global current_model_name, model
    current_model_name = model_name
    
    if api_is_configured:
        try:
            # Buat instance model menggunakan syntax SDK lama
            model = genai.GenerativeModel(
                model_name=current_model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
            print(f"Model Gemini diatur ke: {current_model_name}")
        except Exception as e:
            print(f"Gagal membuat instance model {current_model_name}: {e}")
            model = None 
    else:
         print("API Key belum dikonfigurasi, 'set_model' ditunda.")


# --- FUNGSI DIPERBARUI ---
def extract_data_from_images(image_paths: list[str]):
    """
    Mengirim BEBERAPA gambar ke API menggunakan 'model.generate_content()'.
    """
    
    if not api_is_configured or model is None:
        return False, "Gemini API belum dikonfigurasi atau model gagal dimuat.\n\nSilakan periksa API Key dan pilihan Model Anda."

    try:
        loaded_images = []
        for path in image_paths:
            print(f"Memuat gambar: {path}...")
            img = Image.open(path)
            loaded_images.append(img)
            
        if not loaded_images:
            return False, "Tidak ada gambar yang dipilih."

        prompt_parts = loaded_images + [
            "Tolong ekstrak data dari gambar-gambar ini sesuai dengan aturan dan skema JSON yang telah ditentukan."
        ]

        # Konfigurasi JSON Mode (Syntax SDK lama)
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA 
        )
        
        print(f"Memanggil API menggunakan model: {current_model_name}...")
        
        # Panggil API menggunakan syntax SDK lama
        response = model.generate_content(
            prompt_parts,
            generation_config=generation_config
        )
        
        print(f"Respon JSON API: {response.text}")
        data_dict = json.loads(response.text)
        
        return True, data_dict

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        if "response" in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Detail Error: {response.prompt_feedback}")
        return False, f"Terjadi kesalahan saat memproses gambar: {e}"