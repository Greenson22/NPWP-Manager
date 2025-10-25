# main.py
# File utama untuk menjalankan aplikasi

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QAction, QFont

import db_manager
from form_widget import FormWidget
from view_widget import ViewWidget
from detail_widget import DetailWidget # <-- 1. IMPOR WIDGET BARU

class MainWindow(QMainWindow):
    """Jendela utama aplikasi."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP')
        self.setGeometry(100, 100, 800, 700)

        self.setup_menu()
        self.setup_main_widgets()
        
        self.show_add_new_form() 

    # --- FUNGSI setup_menu (TETAP SAMA) ---
    def setup_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu('File')
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

    # --- FUNGSI DIPERBARUI ---
    def setup_main_widgets(self):
        """Membuat QStackedWidget dan menambahkan semua halaman."""
        
        self.stacked_widget = QStackedWidget()
        
        # Buat instance dari semua halaman
        self.form_page = FormWidget()
        self.view_page = ViewWidget()
        self.detail_page = DetailWidget() # <-- 2. BUAT INSTANCE HALAMAN DETAIL
        
        # Tambahkan halaman ke stacked widget
        self.stacked_widget.addWidget(self.form_page)
        self.stacked_widget.addWidget(self.view_page)
        self.stacked_widget.addWidget(self.detail_page) # <-- 3. TAMBAHKAN KE STACK

        self.setCentralWidget(self.stacked_widget)

        # --- Hubungkan Sinyal ---
        
        # Sinyal dari Form
        self.form_page.data_saved.connect(self.handle_data_saved)
        
        # Sinyal dari View/Tabel
        self.view_page.edit_requested.connect(self.handle_edit_request)
        self.view_page.delete_requested.connect(self.handle_delete_request)
        self.view_page.detail_requested.connect(self.handle_detail_request) # <-- 4. HUBUNGKAN SINYAL BARU
        
        # Sinyal dari Detail
        self.detail_page.back_requested.connect(self.show_view_page) # <-- 5. HUBUNGKAN SINYAL KEMBALI

    # --- FUNGSI SLOT (Logika Aplikasi) ---

    def navigate_to_form_page(self):
        self.stacked_widget.setCurrentWidget(self.form_page)

    def show_view_page(self):
        """Beralih ke tampilan tabel dan me-refresh datanya."""
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

    # --- FUNGSI SLOT BARU ---
    def handle_detail_request(self, user_id):
        """Mempersiapkan dan menampilkan halaman detail."""
        print(f"Menerima permintaan detail untuk ID: {user_id}")
        self.detail_page.load_data(user_id)
        self.stacked_widget.setCurrentWidget(self.detail_page)
        self.setWindowTitle(f'Aplikasi Pendaftaran NPWP - Detail Data (ID: {user_id})')

    # --- FUNGSI DIPERBARUI ---
    def handle_delete_request(self, user_id):
        print(f"Menerima permintaan hapus untuk ID: {user_id}")
        
        success, data = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", data)
            return

        nama = data['nama']
        nik = data['nik']
        
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus data:\n\n"
            f"Nama: {nama}\n"
            f"NIK: {nik}\n\n"
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

# --- Main execution (TETAP SAMA) ---
if __name__ == '__main__':
    db_manager.init_db() 
    
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion") 
    
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())