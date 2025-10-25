# form_widget.py
# Berisi QWidget dengan TABS untuk formulir pendaftaran dan BANTUAN AI

import os
import shutil
import platform
import subprocess
import json
from pathlib import Path

# --- IMPOR PYQT ---
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QTextEdit, QPushButton, QMessageBox, QGroupBox, QDateEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QFileDialog, 
    QScrollArea, QCheckBox, QTabWidget, QApplication
)
# --- IMPOR DIPERBARUI ---
from PyQt6.QtCore import QDate, QRegularExpression, pyqtSignal, pyqtSlot, Qt

from PyQt6.QtGui import QRegularExpressionValidator

# --- IMPOR KUSTOM ---
import db_manager
from config import BASE_DOC_FOLDER, FIELD_UNTUK_INSERT

# --- KELAS FORM WIDGET (DIPERBARUI DENGAN TABS) ---
class FormWidget(QWidget): 
    data_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.current_edit_id = None
        self.current_doc_folder = None
        self.files_to_add = set()
        self.files_to_remove = set()
        
        # --- DAFTAR STATUS HUBUNGAN BARU ---
        self.STATUS_HUBUNGAN_LIST = [
            "", "Kepala Keluarga", "Suami", "Istri", "Anak", "Menantu", 
            "Orang tua", "Mertua", "Family Lain", "Pembantu", "Lainnya"
        ]
        
        self.tab_widget = QTabWidget() 
        
        # --- DATA BARU UNTUK AI PROMPT ---
        self.ai_system_instruction = ""
        self.ai_json_schema = ""
        self._generate_ai_prompt_assets()
        # --- AKHIR DATA BARU ---
        
        self.init_ui()

    def _generate_ai_prompt_assets(self):
        """Membangun string prompt dan skema JSON berdasarkan config.py"""
        
        self.ai_system_instruction = (
            "Anda adalah asisten OCR yang ahli dalam membaca dokumen kependudukan Indonesia (KTP dan KK).\n"
            "Tugas Anda adalah menganalisis gambar, menggabungkan data dari KTP dan KK, dan mengisi skema JSON yang disediakan.\n\n"
            "ATURAN PRIORITAS:\n"
            "1. Gunakan KTP sebagai sumber utama (prioritas 1) untuk: 'nama', 'nik', 'tempat_lahir', 'tanggal_lahir', 'alamat', 'pekerjaan'.\n"
            "2. Gunakan Kartu Keluarga (KK) sebagai sumber utama (prioritas 1) untuk: 'no_kk', 'nik_kk' (NIK Kepala Keluarga), dan 'status_hubungan'.\n"
            "3. Jika data di KTP tidak jelas (misal 'alamat' terpotong), Anda boleh menggunakan data dari KK sebagai cadangan (prioritas 2).\n"
            "4. Jika 'status_hubungan' adalah 'Kepala Keluarga', maka 'nik_kk' harus sama dengan 'nik' orang tersebut.\n"
            "5. Untuk data yang tidak ada di KTP/KK (seperti 'email', 'password', 'status', 'keterangan', 'catatan'), kembalikan string kosong \"\".\n"
            "6. 'nama_ibu' biasanya hanya ada di KK.\n"
            "7. Pastikan 'tanggal_lahir' dalam format YYYY-MM-DD."
        )

        # Buat properti skema dari FIELD_UNTUK_INSERT di config.py
        properties = {}
        for field in FIELD_UNTUK_INSERT:
            properties[field] = {"type": "string"}
        
        # Tambahkan deskripsi khusus
        properties['tanggal_lahir']['description'] = "Format YYYY-MM-DD"
        properties['status_hubungan']['description'] = "Contoh: Kepala Keluarga, Istri, Anak"
        properties['status']['description'] = "Contoh: Berhasil, Pengawasan, Gagal (Kosongkan jika tidak ada)"
        
        # Tentukan skema
        schema = {
            "type": "object",
            "properties": properties,
            "required": ["nama", "nik"] # Hanya perlukan yang utama
        }
        
        # Ubah dict skema menjadi string JSON yang rapi
        self.ai_json_schema = json.dumps(schema, indent=2)

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget) # Tambahkan Tab Widget ke layout utama

        # --- Buat Tab 1: Formulir Pendaftaran ---
        form_tab = QWidget()
        form_tab_layout = QVBoxLayout(form_tab)
        
        form_scroll_area = QScrollArea()
        form_scroll_area.setWidgetResizable(True)
        
        form_content_widget = QWidget()
        form_scroll_area.setWidget(form_content_widget)
        
        form_layout = QVBoxLayout(form_content_widget)

        nik_validator = QRegularExpressionValidator(QRegularExpression(r'\d{16}'))

        # --- Grup 1: Status Pendaftaran ---
        group_status = QGroupBox("Status Pendaftaran")
        layout_status = QFormLayout()
        self.status_input = QComboBox()
        self.status_input.addItems(["", "Berhasil", "Pengawasan", "Gagal"])
        self.keterangan_input = QLineEdit()
        self.catatan_input = QTextEdit()
        self.catatan_input.setFixedHeight(60) 
        self.catatan_input.setPlaceholderText("Tambahkan catatan internal di sini...")
        layout_status.addRow("Status:", self.status_input)
        layout_status.addRow("Keterangan:", self.keterangan_input)
        layout_status.addRow("Catatan:", self.catatan_input)
        group_status.setLayout(layout_status)
        
        # --- Grup 2: Data Diri ---
        group_data_diri = QGroupBox("Data Diri Pemohon")
        layout_data_diri = QFormLayout()
        self.nama_input = QLineEdit()
        self.status_hubungan_input = QComboBox()
        self.status_hubungan_input.addItems(self.STATUS_HUBUNGAN_LIST)
        self.nik_input = QLineEdit()
        self.nik_input.setValidator(nik_validator)
        self.nik_input.setPlaceholderText("16 digit NIK")
        self.nik_kk_input = QLineEdit()
        self.nik_kk_input.setValidator(nik_validator)
        self.nik_kk_input.setPlaceholderText("16 digit NIK Kepala Keluarga")
        self.no_kk_input = QLineEdit()
        self.no_kk_input.setValidator(nik_validator)
        self.no_kk_input.setPlaceholderText("16 digit Nomor Kartu Keluarga")
        self.tempat_lahir_input = QLineEdit()
        self.tanggal_lahir_input = QDateEdit()
        self.tanggal_lahir_input.setDate(QDate.currentDate().addYears(-20))
        self.tanggal_lahir_input.setCalendarPopup(True)
        self.tanggal_lahir_input.setDisplayFormat("dd MMMM yyyy")
        self.alamat_input = QTextEdit()
        self.alamat_input.setFixedHeight(80)
        self.pekerjaan_input = QLineEdit()
        self.nama_ibu_input = QLineEdit()
        layout_data_diri.addRow("Nama Lengkap:", self.nama_input)
        layout_data_diri.addRow("Status Hub. Keluarga:", self.status_hubungan_input)
        layout_data_diri.addRow("NIK:", self.nik_input)
        layout_data_diri.addRow("NIK Kepala Keluarga:", self.nik_kk_input)
        layout_data_diri.addRow("Nomor Kartu Keluarga:", self.no_kk_input)
        layout_data_diri.addRow("Tempat Lahir:", self.tempat_lahir_input)
        layout_data_diri.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        layout_data_diri.addRow("Alamat:", self.alamat_input)
        layout_data_diri.addRow("Pekerjaan:", self.pekerjaan_input)
        layout_data_diri.addRow("Nama Ibu Kandung:", self.nama_ibu_input)
        group_data_diri.setLayout(layout_data_diri)
        
        self.status_hubungan_input.currentIndexChanged.connect(self.on_status_hubungan_changed)
        self.nik_input.textChanged.connect(self.on_nik_changed)

        # --- Grup 3: Akun & Kontak ---
        group_akun = QGroupBox("Akun dan Kontak")
        layout_akun = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("contoh@email.com")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_checkbox = QCheckBox("Tampilkan")
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_checkbox)
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setPlaceholderText("08...")
        layout_akun.addRow("Email:", self.email_input)
        layout_akun.addRow("Password:", password_layout)
        layout_akun.addRow("Nomor HP:", self.no_hp_input)
        group_akun.setLayout(layout_akun)

        # --- Grup 4: Manajemen Dokumen ---
        group_dokumen = QGroupBox("Manajemen Dokumen")
        layout_dokumen = QVBoxLayout()
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout_tombol_doc = QHBoxLayout()
        self.add_file_btn = QPushButton("Tambah File...")
        self.add_file_btn.clicked.connect(self.on_add_files)
        self.remove_file_btn = QPushButton("Hapus File Terpilih")
        self.remove_file_btn.clicked.connect(self.on_remove_file)
        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 6px; border-radius: 4px;")
        self.open_folder_btn.clicked.connect(self.on_open_folder)
        layout_tombol_doc.addWidget(self.add_file_btn)
        layout_tombol_doc.addWidget(self.remove_file_btn)
        layout_tombol_doc.addStretch()
        layout_tombol_doc.addWidget(self.open_folder_btn)
        layout_dokumen.addLayout(layout_tombol_doc)
        layout_dokumen.addWidget(self.file_list_widget)
        group_dokumen.setLayout(layout_dokumen)

        # --- Tombol Aksi ---
        layout_tombol = QHBoxLayout()
        self.simpan_btn = QPushButton("Simpan Data")
        self.simpan_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")
        self.simpan_btn.clicked.connect(self.simpan_data)
        self.bersihkan_btn = QPushButton("Bersihkan Form")
        self.bersihkan_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
        self.bersihkan_btn.clicked.connect(self.bersihkan_form)
        layout_tombol.addWidget(self.bersihkan_btn)
        layout_tombol.addWidget(self.simpan_btn)

        # --- Tambahkan semua grup ke layout form ---
        form_layout.addWidget(group_status)
        form_layout.addWidget(group_data_diri)
        form_layout.addWidget(group_akun)
        form_layout.addWidget(group_dokumen)
        form_layout.addLayout(layout_tombol)
        
        # --- Masukkan Scroll Area ke Tab 1 ---
        form_tab_layout.addWidget(form_scroll_area)
        
        # --- Buat Tab 2: Bantuan AI (Eksternal) ---
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        self.setup_ai_tab(ai_layout) # Panggil fungsi helper baru

        # --- Tambahkan kedua tab ke QTabWidget ---
        self.tab_widget.addTab(form_tab, "Formulir Pendaftaran")
        self.tab_widget.addTab(ai_tab, "🤖 Bantuan AI (Eksternal)")

    # --- FUNGSI HELPER BARU UNTUK TAB AI ---
    def setup_ai_tab(self, layout: QVBoxLayout):
        """Membangun UI untuk tab Bantuan AI."""
        
        # --- Grup 1: Salin Prompt ---
        group_prompt = QGroupBox("Langkah 1: Salin Prompt untuk Google AI Studio")
        layout_prompt = QVBoxLayout()
        
        prompt_label = QLabel("Gunakan prompt dan skema JSON ini di AI Studio untuk mengekstrak data dari gambar KTP dan KK Anda.")
        prompt_label.setWordWrap(True)
        
        self.ai_prompt_display = QTextEdit()
        self.ai_prompt_display.setReadOnly(True)
        # Gabungkan instruksi dan skema untuk disalin
        full_prompt_text = f"--- INSTRUKSI SISTEM ---\n{self.ai_system_instruction}\n\n--- SKEMA JSON (Gunakan di 'JSON Mode') ---\n{self.ai_json_schema}"
        self.ai_prompt_display.setPlainText(full_prompt_text)
        self.ai_prompt_display.setFixedHeight(200) # Batasi tinggi
        
        self.ai_copy_prompt_btn = QPushButton("Salin Prompt & Skema")
        self.ai_copy_prompt_btn.setStyleSheet("background-color: #0275d8; color: white; padding: 8px; border-radius: 4px;")
        self.ai_copy_prompt_btn.clicked.connect(self.on_copy_prompt)
        
        layout_prompt.addWidget(prompt_label)
        layout_prompt.addWidget(self.ai_prompt_display)
        layout_prompt.addWidget(self.ai_copy_prompt_btn)
        group_prompt.setLayout(layout_prompt)
        
        # --- Grup 2: Impor Hasil ---
        group_import = QGroupBox("Langkah 2: Impor Hasil JSON")
        layout_import = QVBoxLayout()
        
        import_label = QLabel("Tempelkan (paste) hasil JSON yang Anda dapatkan dari AI Studio ke dalam kotak di bawah ini.")
        import_label.setWordWrap(True)
        
        self.ai_json_input = QTextEdit()
        self.ai_json_input.setPlaceholderText("Contoh: {\n  \"nama\": \"Budi Santoso\",\n  \"nik\": \"317...\"\n  ...\n}")
        
        self.ai_import_json_btn = QPushButton("Impor Data JSON")
        self.ai_import_json_btn.setStyleSheet("background-color: #5cb85c; color: white; padding: 8px; border-radius: 4px;")
        self.ai_import_json_btn.clicked.connect(self.on_import_json)
        
        layout_import.addWidget(import_label)
        layout_import.addWidget(self.ai_json_input)
        layout_import.addWidget(self.ai_import_json_btn)
        group_import.setLayout(layout_import)

        layout.addWidget(group_prompt)
        layout.addWidget(group_import)
        layout.addStretch()

    @pyqtSlot()
    def on_copy_prompt(self):
        """Menyalin teks dari ai_prompt_display ke clipboard."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.ai_prompt_display.toPlainText())
            QMessageBox.information(self, "Sukses", "Prompt dan Skema JSON telah disalin ke clipboard.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyalin: {e}")

    @pyqtSlot()
    def on_import_json(self):
        """Mengambil JSON dari input, mem-parse, dan mengisi formulir."""
        json_text = self.ai_json_input.toPlainText()
        if not json_text:
            QMessageBox.warning(self, "Input Kosong", "Kotak input JSON masih kosong.")
            return
            
        try:
            # Hapus ```json ... ``` jika ada
            if json_text.strip().startswith("```json"):
                json_text = json_text.strip()[7:-3].strip()
            
            data = json.loads(json_text)
            
            self.populate_form_with_ai_data(data)
            
            QMessageBox.information(self, "Sukses", "Data JSON berhasil diimpor ke formulir!")
            self.tab_widget.setCurrentIndex(0) # Pindah ke tab formulir
            self.ai_json_input.clear() # Bersihkan input
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error JSON", f"Format JSON tidak valid. Pastikan Anda menyalin seluruh blok JSON.\n\nError: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat mengimpor: {e}")

    # --- AKHIR FUNGSI HELPER BARU ---

    @pyqtSlot(bool)
    def toggle_password_visibility(self, checked):
        """Mengubah mode tampilan QLineEdit password."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def on_status_hubungan_changed(self):
        is_kepala_keluarga = (self.status_hubungan_input.currentText() == "Kepala Keluarga")
        self.nik_kk_input.setReadOnly(is_kepala_keluarga)
        if is_kepala_keluarga:
            self.nik_kk_input.setText(self.nik_input.text())
        else:
            self.nik_kk_input.clear()

    def on_nik_changed(self, text):
        if self.status_hubungan_input.currentText() == "Kepala Keluarga":
            self.nik_kk_input.setText(text)

    # --- FUNGSI POPULATE (DIBUAT KEMBALI) ---
    def populate_form_with_ai_data(self, data: dict):
        """Mengisi field formulir menggunakan data dari dict (JSON)."""
        print(f"Mengisi form dengan data: {data}")
        
        # Gunakan .get() untuk keamanan jika kunci tidak ada
        if data.get('nama'): self.nama_input.setText(data.get('nama'))
        if data.get('nik'): self.nik_input.setText(data.get('nik'))
        if data.get('nik_kk'): self.nik_kk_input.setText(data.get('nik_kk'))
        if data.get('no_kk'): self.no_kk_input.setText(data.get('no_kk'))
        if data.get('tempat_lahir'): self.tempat_lahir_input.setText(data.get('tempat_lahir'))
        if data.get('alamat'): self.alamat_input.setPlainText(data.get('alamat'))
        if data.get('pekerjaan'): self.pekerjaan_input.setText(data.get('pekerjaan'))
        if data.get('nama_ibu'): self.nama_ibu_input.setText(data.get('nama_ibu'))
        
        # Field opsional
        if data.get('email'): self.email_input.setText(data.get('email'))
        if data.get('password'): self.password_input.setText(data.get('password'))
        if data.get('no_hp'): self.no_hp_input.setText(data.get('no_hp'))
        if data.get('catatan'): self.catatan_input.setPlainText(data.get('catatan'))
        if data.get('keterangan'): self.keterangan_input.setText(data.get('keterangan'))

        # Handle ComboBox (Status)
        if data.get('status'):
            index = self.status_input.findText(data.get('status'), Qt.MatchFlag.MatchFixedString)
            if index >= 0: self.status_input.setCurrentIndex(index)
        
        # Handle ComboBox (Status Hubungan)
        if data.get('status_hubungan'):
            index_hub = self.status_hubungan_input.findText(data.get('status_hubungan'), Qt.MatchFlag.MatchFixedString)
            if index_hub >= 0:
                self.status_hubungan_input.setCurrentIndex(index_hub)
            else:
                # Jika tidak ada, coba 'Lainnya'
                index_lainnya = self.status_hubungan_input.findText("Lainnya")
                if index_lainnya >= 0:
                     self.status_hubungan_input.setCurrentIndex(index_lainnya)
        
        # Handle Tanggal Lahir
        if data.get('tanggal_lahir'):
            tgl = QDate.fromString(data.get('tanggal_lahir'), "yyyy-MM-dd")
            if not tgl.isValid():
                tgl = QDate.fromString(data.get('tanggal_lahir'), "dd-MM-yyyy")
            if tgl.isValid():
                self.tanggal_lahir_input.setDate(tgl)
            else:
                print(f"Format tanggal dari AI tidak valid: {data.get('tanggal_lahir')}")
        
        # Panggil handler secara manual untuk update state NIK KK
        self.on_status_hubungan_changed()

    def on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Pilih Dokumen", "", "Semua File (*.*)")
        if files:
            for file_path in files:
                self.files_to_add.add(file_path)
                item = QListWidgetItem(f"[BARU] {file_path}")
                self.file_list_widget.addItem(item)
    
    def on_remove_file(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            item_text = item.text()
            if item_text.startswith("[BARU] "):
                self.files_to_add.discard(item_text.replace("[BARU] ", ""))
            else:
                self.files_to_remove.add(item_text)
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

    def on_open_folder(self):
        if self.current_doc_folder and self.current_doc_folder.exists():
            path = str(self.current_doc_folder.resolve())
            try:
                if platform.system() == "Windows": os.startfile(path)
                elif platform.system() == "Darwin": subprocess.Popen(["open", path])
                else: subprocess.Popen(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Tidak bisa membuka folder: {e}")
        else:
            QMessageBox.information(self, "Info", "Folder belum ada. Simpan data.")

    def _populate_file_list(self):
        self.file_list_widget.clear()
        if self.current_doc_folder and self.current_doc_folder.exists():
            for file_path in self.current_doc_folder.iterdir():
                if file_path.is_file(): self.file_list_widget.addItem(file_path.name)
        
    def load_data_for_edit(self, user_id):
        self.bersihkan_form()
        success, data_row = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {data_row}")
            return
        
        # Isi semua field dari data_row
        self.nama_input.setText(data_row['nama'])
        self.status_input.setCurrentText(data_row['status'])
        self.keterangan_input.setText(data_row['keterangan'])
        self.catatan_input.setPlainText(data_row['catatan'] or "")
        self.status_hubungan_input.setCurrentText(data_row['status_hubungan'])
        self.nik_input.setText(data_row['nik'])
        self.nik_kk_input.setText(data_row['nik_kk'])
        self.no_kk_input.setText(data_row['no_kk'])
        self.tempat_lahir_input.setText(data_row['tempat_lahir'])
        tgl = QDate.fromString(data_row['tanggal_lahir'], "yyyy-MM-dd")
        self.tanggal_lahir_input.setDate(tgl)
        self.alamat_input.setPlainText(data_row['alamat'])
        self.pekerjaan_input.setText(data_row['pekerjaan'])
        self.nama_ibu_input.setText(data_row['nama_ibu'])
        self.email_input.setText(data_row['email'])
        self.password_input.setText(data_row['password'])
        self.no_hp_input.setText(data_row['no_hp'])
        
        self.current_edit_id = user_id
        self.simpan_btn.setText("Update Data")
        self.current_doc_folder = Path(BASE_DOC_FOLDER) / data_row['nik']
        self._populate_file_list()
        
        # Pastikan mulai di tab formulir (indeks 0)
        self.tab_widget.setCurrentIndex(0)
        
        # Panggil handler secara manual untuk mengatur state read-only NIK KK
        self.on_status_hubungan_changed()

    def simpan_data(self):
        nik = self.nik_input.text()
        if not self.nama_input.text() or not nik:
            QMessageBox.warning(self, "Input Error", "Nama dan NIK wajib diisi!")
            return
        if not self.nik_input.hasAcceptableInput():
            QMessageBox.warning(self, "Input Error", "Format NIK tidak valid.")
            return
            
        data = {
            "nama": self.nama_input.text(),
            "status": self.status_input.currentText(),
            "keterangan": self.keterangan_input.text(),
            "catatan": self.catatan_input.toPlainText(),
            "status_hubungan": self.status_hubungan_input.currentText(), 
            "nik": nik, "nik_kk": self.nik_kk_input.text(), "no_kk": self.no_kk_input.text(),
            "tempat_lahir": self.tempat_lahir_input.text(),
            "tanggal_lahir": self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            "alamat": self.alamat_input.toPlainText(),
            "pekerjaan": self.pekerjaan_input.text(),
            "nama_ibu": self.nama_ibu_input.text(),
            "email": self.email_input.text(), "password": self.password_input.text(), 
            "no_hp": self.no_hp_input.text(),
            "files_to_add": self.files_to_add, "files_to_remove": self.files_to_remove
        }
        
        if self.current_edit_id is None:
            success, message = db_manager.save_data(data)
        else:
            data['old_nik'] = self.current_doc_folder.name if self.current_doc_folder else nik
            success, message = db_manager.update_data(self.current_edit_id, data)
            
        if success:
            QMessageBox.information(self, "Sukses", message)
            self.bersihkan_form()
            self.data_saved.emit()
        else:
            QMessageBox.critical(self, "Database Error", message)

    def bersihkan_form(self):
        # Bersihkan semua field input
        self.nama_input.clear()
        self.status_input.setCurrentIndex(0)
        self.keterangan_input.clear()
        self.catatan_input.clear()
        self.status_hubungan_input.setCurrentIndex(0)
        self.nik_input.clear()
        self.nik_kk_input.clear()
        self.no_kk_input.clear()
        self.tempat_lahir_input.clear()
        self.tanggal_lahir_input.setDate(QDate.currentDate().addYears(-20))
        self.alamat_input.clear()
        self.pekerjaan_input.clear()
        self.nama_ibu_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.show_password_checkbox.setChecked(False)
        self.no_hp_input.clear()
        
        # Bersihkan data manajemen file
        self.file_list_widget.clear()
        self.files_to_add.clear()
        self.files_to_remove.clear()
        self.current_doc_folder = None
        
        # Bersihkan data AI
        if hasattr(self, 'ai_json_input'):
            self.ai_json_input.clear()
        
        # Reset state
        self.current_edit_id = None
        self.simpan_btn.setText("Simpan Data")
        self.nik_kk_input.setReadOnly(False)
        
        # Kembali ke tab formulir
        self.tab_widget.setCurrentIndex(0)

# --- Perlu tambahkan import QLabel di atas ---
from PyQt6.QtWidgets import QLabel