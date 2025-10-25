# gemini_parser.py
# Mengurus semua logika untuk memanggil Gemini API
# VERSI 4.0 - Eksklusif menggunakan SDK baru (genai.Client)

try:
    from google import genai
    from google.genai.types import GenerationConfig
except ImportError:
    print("="*50)
    print("ERROR: Library 'google-genai' tidak ditemukan.")
    print("Silakan jalankan: pip install google-genai")
    print("="*50)
    # Hentikan program jika library inti tidak ada
    raise

from PIL import Image
import json
import os # <-- Tambahkan import os untuk basename

# --- Variabel Global ---
client = None
api_is_configured = False
current_model_name = "" 
api_init_error_message = "" # <-- VARIABEL BARU UNTUK MENYIMPAN ERROR

# Skema JSON (tidak berubah)
# --- DIPERBARUI ---
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "nama": {"type": "string"},
        "status_hubungan": {"type": "string", "description": "Status hubungan keluarga dari KK, misal: Kepala Keluarga, Istri, Anak, dll."},
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
# --- DIPERBARUI ---
SYSTEM_INSTRUCTION = (
    "Anda adalah asisten OCR yang ahli dalam membaca dokumen kependudukan Indonesia (KTP dan KK).\n"
    "Tugas Anda adalah menganalisis gambar, menggabungkan data dari KTP dan KK, dan mengisi skema JSON yang disediakan.\n\n"
    "ATURAN PRIORITAS:\n"
    "1. Gunakan KTP sebagai sumber utama (prioritas 1) untuk: 'nama', 'nik', 'tempat_lahir', 'tanggal_lahir', 'alamat'.\n"
    "2. Gunakan Kartu Keluarga (KK) sebagai sumber utama (prioritas 1) untuk: 'no_kk', 'nik_kk' (NIK Kepala Keluarga), dan 'status_hubungan'.\n"
    "3. Jika data di KTP tidak jelas (misal 'alamat' terpotong), Anda boleh menggunakan data dari KK sebagai cadangan (prioritas 2).\n"
    "4. Jika 'status_hubungan' adalah 'Kepala Keluarga', maka 'nik_kk' harus sama dengan 'nik' orang tersebut.\n"
    "5. Jika data tidak ditemukan di gambar manapun, kembalikan string kosong \"\"."
)
# --- AKHIR PERUBAHAN ---


def init_api(api_key: str):
    """
    Menginisialisasi Gemini API Client (SDK Baru) dengan key.
    """
    global client, api_is_configured, api_init_error_message # <-- Tambahkan var baru
    
    if api_key:
        try:
            # Gunakan API key untuk mengautentikasi client
            genai.configure(api_key=api_key) 
            client = genai.Client()
            client.models.list() # Tes koneksi dengan mengambil daftar model
            
            api_is_configured = True
            api_init_error_message = "" # Hapus error jika sukses
            print("Gemini API (Client SDK) berhasil dikonfigurasi.")
            
        except Exception as e:
            print(f"Konfigurasi Gemini (Client SDK) gagal: {e}")
            api_is_configured = False
            # --- BARIS YANG DIPERBARUI ---
            # Simpan pesan error spesifik agar bisa dibaca UI
            api_init_error_message = f"Koneksi gagal: {e}" 
            # ---------------------------
            
    else:
        api_is_configured = False
        # --- BARIS YANG DIPERBARUI ---
        api_init_error_message = "API Key tidak ditemukan. Silakan masukkan API Key melalui menu 'File' > 'Konfigurasi API Key'."
        # ---------------------------
        print("Gemini API Key tidak ditemukan. Fitur AI akan dinonaktifkan.")

def set_model(model_name: str):
    """
    Dipanggil oleh main.py untuk menyimpan nama model yang akan digunakan.
    """
    global current_model_name
    current_model_name = model_name
    print(f"Model Gemini diatur ke: {current_model_name}")


def extract_data_from_images(image_paths: list[str]):
    """
    Mengirim BEBERAPA gambar ke API menggunakan 'client.models.generate_content()'.
    """
    
    if not api_is_configured or client is None:
        # Gunakan pesan error yang tersimpan jika ada
        error_msg = api_init_error_message or "Gemini API belum dikonfigurasi."
        return False, f"{error_msg}\n\nSilakan masukkan API Key Anda melalui menu 'File' > 'Konfigurasi API Key'."

    if not current_model_name:
        return False, "Model Gemini belum dipilih. Silakan pilih model dari menu 'Pengaturan'."

    try:
        loaded_images = []
        for path in image_paths:
            print(f"Memuat gambar: {path}...")
            # Unggah file ke API untuk mendapatkan 'handle'
            uploaded_file = client.files.upload(
                path=path,
                display_name=os.path.basename(path)
            )
            loaded_images.append(uploaded_file)
            
        if not loaded_images:
            return False, "Tidak ada gambar yang dipilih."

        # Buat prompt 'contents' menggunakan referensi file yang diunggah
        prompt_parts = loaded_images + [
            "Tolong ekstrak data dari gambar-gambar ini (KTP dan KK) sesuai dengan aturan dan skema JSON yang telah ditentukan."
        ]

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA 
        )
        
        print(f"Memanggil API menggunakan model: {current_model_name}...")
        
        response = client.models.generate_content(
            model=current_model_name,
            contents=prompt_parts,           
            system_instruction=SYSTEM_INSTRUCTION, 
            generation_config=generation_config
        )
        
        # Hapus file setelah digunakan (opsional, tapi praktik yang baik)
        for f in loaded_images:
            try:
                client.files.delete(f)
            except Exception as e:
                print(f"Gagal menghapus file sementara {f.name}: {e}")
        
        print(f"Respon JSON API: {response.text}")
        data_dict = json.loads(response.text)
        
        return True, data_dict

    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        if "response" in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Detail Error: {response.prompt_feedback}")
        return False, f"Terjadi kesalahan saat memproses gambar: {e}"