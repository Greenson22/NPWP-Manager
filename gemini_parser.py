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

# --- Variabel Global ---
client = None
api_is_configured = False
current_model_name = "" 

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


def init_api(api_key: str):
    """
    Menginisialisasi Gemini API Client (SDK Baru) dengan key.
    """
    global client, api_is_configured
    
    if api_key:
        try:
            # Gunakan API key untuk mengautentikasi client
            # (Asumsi SDK baru menggunakan 'api_key' saat inisialisasi client
            # atau mengambil dari os.environ yang diatur main.py)
            genai.configure(api_key=api_key) 
            client = genai.Client()
            client.models.list() 
            api_is_configured = True
            print("Gemini API (Client SDK) berhasil dikonfigurasi.")
        except Exception as e:
            print(f"Konfigurasi Gemini (Client SDK) gagal: {e}")
            api_is_configured = False
    else:
        api_is_configured = False
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
        return False, "Gemini API belum dikonfigurasi.\n\nSilakan masukkan API Key Anda melalui menu 'File' > 'Konfigurasi API Key'."

    if not current_model_name:
        return False, "Model Gemini belum dipilih. Silakan pilih model dari menu 'Pengaturan'."

    try:
        loaded_images = []
        for path in image_paths:
            print(f"Memuat gambar: {path}...")
            # Unggah file ke API untuk mendapatkan 'handle'
            # Ini adalah cara yang lebih baik untuk SDK baru
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