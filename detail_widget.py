# detail_widget.py
# Berisi QWidget untuk MENAMPILKAN detail data (read-only)

import os
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QTextEdit, QPushButton, QMessageBox, QGroupBox, QDateEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
import db_manager
from config import BASE_DOC_FOLDER

class DetailWidget(QScrollArea):
    # Sinyal untuk memberitahu main window agar kembali ke tabel
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.content_widget = QWidget()
        self.setWidgetResizable(True)
        self.setWidget(self.content_widget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.current_doc_folder = None
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        main_layout = QVBoxLayout(self.content_widget)

        # Buat semua widget input, tapi set read-only
        
        # --- Grup 1: Status Pendaftaran ---
        group_status = QGroupBox("Status Pendaftaran")
        layout_status = QFormLayout()
        self.status_display = QLineEdit()
        self.status_display.setReadOnly(True)
        self.keterangan_display = QLineEdit()
        self.keterangan_display.setReadOnly(True)
        layout_status.addRow("Status:", self.status_display)
        layout_status.addRow("Keterangan:", self.keterangan_display)
        group_status.setLayout(layout_status)
        
        # --- Grup 2: Data Diri ---
        group_data_diri = QGroupBox("Data Diri Pemohon")
        layout_data_diri = QFormLayout()
        self.nama_display = QLineEdit()
        self.nama_display.setReadOnly(True)
        self.nik_display = QLineEdit()
        self.nik_display.setReadOnly(True)
        self.nik_kk_display = QLineEdit()
        self.nik_kk_display.setReadOnly(True)
        self.no_kk_display = QLineEdit()
        self.no_kk_display.setReadOnly(True)
        self.tempat_lahir_display = QLineEdit()
        self.tempat_lahir_display.setReadOnly(True)
        self.tanggal_lahir_display = QLineEdit()
        self.tanggal_lahir_display.setReadOnly(True)
        self.alamat_display = QTextEdit()
        self.alamat_display.setReadOnly(True)
        self.alamat_display.setFixedHeight(80)
        self.pekerjaan_display = QLineEdit()
        self.pekerjaan_display.setReadOnly(True)
        self.nama_ibu_display = QLineEdit()
        self.nama_ibu_display.setReadOnly(True)
        
        layout_data_diri.addRow("Nama Lengkap:", self.nama_display)
        layout_data_diri.addRow("NIK:", self.nik_display)
        layout_data_diri.addRow("NIK Kepala Keluarga:", self.nik_kk_display)
        layout_data_diri.addRow("Nomor Kartu Keluarga:", self.no_kk_display)
        layout_data_diri.addRow("Tempat Lahir:", self.tempat_lahir_display)
        layout_data_diri.addRow("Tanggal Lahir:", self.tanggal_lahir_display)
        layout_data_diri.addRow("Alamat:", self.alamat_display)
        layout_data_diri.addRow("Pekerjaan:", self.pekerjaan_display)
        layout_data_diri.addRow("Nama Ibu Kandung:", self.nama_ibu_display)
        group_data_diri.setLayout(layout_data_diri)

        # --- Grup 3: Akun & Kontak ---
        group_akun = QGroupBox("Akun dan Kontak")
        layout_akun = QFormLayout()
        self.email_display = QLineEdit()
        self.email_display.setReadOnly(True)
        self.no_hp_display = QLineEdit()
        self.no_hp_display.setReadOnly(True)
        
        layout_akun.addRow("Email:", self.email_display)
        layout_akun.addRow("Nomor HP:", self.no_hp_display)
        group_akun.setLayout(layout_akun)

        # --- Grup 4: Dokumen ---
        group_dokumen = QGroupBox("Dokumen Tersimpan")
        layout_dokumen = QVBoxLayout()
        self.file_list_widget = QListWidget()
        
        self.open_folder_btn = QPushButton("Buka Folder Dokumen")
        self.open_folder_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 6px; border-radius: 4px;")
        self.open_folder_btn.clicked.connect(self.on_open_folder)
        
        layout_dokumen.addWidget(self.open_folder_btn)
        layout_dokumen.addWidget(self.file_list_widget)
        group_dokumen.setLayout(layout_dokumen)

        # --- Tombol Aksi ---
        layout_tombol = QHBoxLayout()
        self.back_btn = QPushButton("Kembali ke Daftar")
        self.back_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        layout_tombol.addStretch()
        layout_tombol.addWidget(self.back_btn)

        main_layout.addWidget(group_status)
        main_layout.addWidget(group_data_diri)
        main_layout.addWidget(group_akun)
        main_layout.addWidget(group_dokumen)
        main_layout.addLayout(layout_tombol)

    def load_data(self, user_id):
        """Ambil data dari DB dan isi semua field."""
        
        success, data_row = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {data_row}")
            self.back_requested.emit() # Kembali jika gagal
            return
            
        # Isi semua field
        self.status_display.setText(data_row['status'] or "-")
        self.keterangan_display.setText(data_row['keterangan'] or "-")
        self.nama_display.setText(data_row['nama'])
        self.nik_display.setText(data_row['nik'])
        self.nik_kk_display.setText(data_row['nik_kk'] or "-")
        self.no_kk_display.setText(data_row['no_kk'] or "-")
        self.tempat_lahir_display.setText(data_row['tempat_lahir'] or "-")
        self.tanggal_lahir_display.setText(data_row['tanggal_lahir'] or "-")
        self.alamat_display.setPlainText(data_row['alamat'] or "-")
        self.pekerjaan_display.setText(data_row['pekerjaan'] or "-")
        self.nama_ibu_display.setText(data_row['nama_ibu'] or "-")
        self.email_display.setText(data_row['email'] or "-")
        self.no_hp_display.setText(data_row['no_hp'] or "-")

        # Isi daftar file
        self.current_doc_folder = Path(BASE_DOC_FOLDER) / data_row['nik']
        self._populate_file_list()

    def _populate_file_list(self):
        """Helper untuk mengisi list file."""
        self.file_list_widget.clear()
        if self.current_doc_folder and self.current_doc_folder.exists():
            files = [f.name for f in self.current_doc_folder.iterdir() if f.is_file()]
            if files:
                self.file_list_widget.addItems(files)
                self.open_folder_btn.setEnabled(True)
            else:
                self.file_list_widget.addItem("Tidak ada dokumen tersimpan.")
                self.open_folder_btn.setEnabled(True) # Folder ada tapi kosong
        else:
            self.file_list_widget.addItem("Folder dokumen tidak ditemukan.")
            self.open_folder_btn.setEnabled(False) # Folder tidak ada
            
    def on_open_folder(self):
        """Membuka folder dokumen orang ini di file explorer."""
        if self.current_doc_folder and self.current_doc_folder.exists():
            path = str(self.current_doc_folder.resolve())
            try:
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin": # macOS
                    subprocess.Popen(["open", path])
                else: # Linux
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Tidak bisa membuka folder: {e}")
        else:
            QMessageBox.information(self, "Info", "Folder tidak ada.")