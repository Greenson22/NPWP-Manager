# main.py
# File utama untuk menjalankan aplikasi

import sys
import os
from dotenv import load_dotenv, set_key
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox,
    QInputDialog, QLineEdit
)
from PyQt6.QtGui import QAction, QFont

import db_manager
from form_widget import FormWidget
from view_widget import ViewWidget
from detail_widget import DetailWidget
import gemini_parser

# Tentukan nama file env
ENV_FILE_PATH = ".myenv"

class MainWindow(QMainWindow):
    """Jendela utama aplikasi."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP')
        self.setGeometry(100, 100, 800, 700)
        
        self.load_and_init_api() 
        self.setup_menu()
        self.setup_main_widgets()
        
        self.show_add_new_form() 

    def load_and_init_api(self):
        """Memuat API Key dari file .env dan menginisialisasi Gemini."""
        load_dotenv(dotenv_path=ENV_FILE_PATH) 
        api_key = os.environ.get("GOOGLE_API_KEY")
        gemini_parser.init_api(api_key)

    def setup_menu(self):
        """Membuat dan mengatur Menu Bar."""
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu('File')

        config_action = QAction('Konfigurasi API Key...', self)
        config_action.triggered.connect(self.configure_api_key)
        file_menu.addAction(config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Keluar', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        nav_menu = menu_bar.addMenu('Navigasi')
        
        add_data_action = QAction('Tambah Data Pendaftaran', self)
        add_data_action.triggered.connect(self.show_add_new_form) 
        nav_menu.addAction(add_data_action)
        
        view_data_action = QAction('Lihat Data Pendaftaran', self)
        view_data_action.triggered.connect(self.show_view_page)
        nav_menu.addAction(view_data_action)

    def configure_api_key(self):
        """Menampilkan dialog untuk memasukkan/mengedit API Key."""
        
        current_key = os.environ.get("GOOGLE_API_KEY", "")
        
        new_key, ok = QInputDialog.getText(
            self, 
            "Konfigurasi API Key", 
            "Masukkan Google Gemini API Key Anda:", 
            QLineEdit.EchoMode.Password, 
            current_key
        )
        
        if ok and new_key and new_key != current_key:
            try:
                set_key(dotenv_path=ENV_FILE_PATH, key_to_set="GOOGLE_API_KEY", value_to_set=new_key) 
                os.environ["GOOGLE_API_KEY"] = new_key
                gemini_parser.init_api(new_key)
                
                if hasattr(self, 'form_page'):
                    self.form_page.enable_ai_button()

                QMessageBox.information(self, "Sukses", "API Key berhasil disimpan dan diaktifkan.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan API Key: {e}")
        elif ok:
             QMessageBox.information(self, "Info", "API Key tidak berubah.")

    def setup_main_widgets(self):
        self.stacked_widget = QStackedWidget()
        
        self.form_page = FormWidget()
        self.view_page = ViewWidget()
        self.detail_page = DetailWidget()
        
        self.stacked_widget.addWidget(self.form_page)
        self.stacked_widget.addWidget(self.view_page)
        self.stacked_widget.addWidget(self.detail_page)

        self.setCentralWidget(self.stacked_widget)

        self.form_page.data_saved.connect(self.handle_data_saved)
        self.view_page.edit_requested.connect(self.handle_edit_request)
        self.view_page.delete_requested.connect(self.handle_delete_request)
        self.view_page.detail_requested.connect(self.handle_detail_request)
        self.detail_page.back_requested.connect(self.show_view_page)
    
    def navigate_to_form_page(self):
        self.stacked_widget.setCurrentWidget(self.form_page)

    def show_view_page(self):
        self.view_page.load_data() 
        self.stacked_widget.setCurrentWidget(self.view_page)
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Lihat Data')

    def show_add_new_form(self):
        self.form_page.bersihkan_form()
        self.navigate_to_form_page()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Tambah Data')
                
    def handle_data_saved(self):
        self.show_view_page() 

    def handle_edit_request(self, user_id):
        print(f"Menerima permintaan edit untuk ID: {user_id}")
        self.form_page.load_data_for_edit(user_id)
        self.navigate_to_form_page()
        self.setWindowTitle(f'Aplikasi Pendaftaran NPWP - Edit Data (ID: {user_id})')

    def handle_detail_request(self, user_id):
        print(f"Menerima permintaan detail untuk ID: {user_id}")
        self.detail_page.load_data(user_id)
        self.stacked_widget.setCurrentWidget(self.detail_page)
        self.setWindowTitle(f'Aplikasi Pendaftaran NPWP - Detail Data (ID: {user_id})')

    def handle_delete_request(self, user_id):
        print(f"Menerima permintaan hapus untuk ID: {user_id}")
        
        success, data = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", data)
            return

        nama = data['nama']
        nik = data['nik']
        
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus data:\n\nNama: {nama}\nNIK: {nik}\n\n"
            f"Tindakan ini juga akan MENGHAPUS SELURUH FOLDER dokumen terkait secara permanen.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = db_manager.delete_data(user_id)
            if success:
                QMessageBox.information(self, "Sukses", message)
                self.view_page.load_data() 
            else:
                QMessageBox.critical(self, "Error", message)

# --- Main execution ---
if __name__ == '__main__':
    db_manager.init_db() 
    
    app = QApplication(sys.argv) # <-- INI PERBAIKANNYA
    
    app.setStyle("Fusion") 
    
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())