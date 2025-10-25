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

class MainWindow(QMainWindow):
    """Jendela utama aplikasi."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP')
        self.setGeometry(100, 100, 800, 700)

        self.setup_menu()
        self.setup_main_widgets()
        
        self.show_add_new_form() 

    def setup_menu(self):
        # (Fungsi ini tidak berubah)
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

    def setup_main_widgets(self):
        # (Fungsi ini tidak berubah)
        self.stacked_widget = QStackedWidget()
        
        self.form_page = FormWidget()
        self.view_page = ViewWidget()
        
        self.stacked_widget.addWidget(self.form_page)
        self.stacked_widget.addWidget(self.view_page)

        self.setCentralWidget(self.stacked_widget)

        self.form_page.data_saved.connect(self.handle_data_saved)
        self.view_page.edit_requested.connect(self.handle_edit_request)
        self.view_page.delete_requested.connect(self.handle_delete_request)

    # --- FUNGSI SLOT (Logika Aplikasi) ---

    def navigate_to_form_page(self):
        # (Fungsi ini tidak berubah)
        self.stacked_widget.setCurrentWidget(self.form_page)

    def show_view_page(self):
        # (Fungsi ini tidak berubah)
        self.view_page.load_data() 
        self.stacked_widget.setCurrentWidget(self.view_page)
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Lihat Data')

    def show_add_new_form(self):
        # (Fungsi ini tidak berubah)
        self.form_page.bersihkan_form()
        self.navigate_to_form_page()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Tambah Data')
                
    def handle_data_saved(self):
        # (Fungsi ini tidak berubah)
        self.show_view_page() 

    def handle_edit_request(self, user_id):
        # (Fungsi ini tidak berubah)
        print(f"Menerima permintaan edit untuk ID: {user_id}")
        self.form_page.load_data_for_edit(user_id)
        self.navigate_to_form_page()
        self.setWindowTitle(f'Aplikasi Pendaftaran NPWP - Edit Data (ID: {user_id})')

    # --- FUNGSI DIPERBARUI ---
    def handle_delete_request(self, user_id):
        """Menangani permintaan hapus dengan konfirmasi yang lebih baik."""
        print(f"Menerima permintaan hapus untuk ID: {user_id}")
        
        # Ambil data dulu untuk konfirmasi
        success, data = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", data)
            return

        nama = data['nama']
        nik = data['nik']
        
        # Tampilkan kotak konfirmasi
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
            # Jika pengguna setuju, hapus data
            success, message = db_manager.delete_data(user_id)
            if success:
                QMessageBox.information(self, "Sukses", message)
                self.view_page.load_data() # Refresh tabel
            else:
                QMessageBox.critical(self, "Error", message)


# --- Main execution ---
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