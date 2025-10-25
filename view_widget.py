# view_widget.py
# Berisi kelas QWidget untuk menampilkan data dalam tabel

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QHBoxLayout  # <-- INI ADALAH PERBAIKANNYA
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction

import db_manager 

class ViewWidget(QWidget):
    """Widget untuk menampilkan data dalam tabel."""
    
    # Sinyal tetap sama
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inisialisasi UI dengan menu klik kanan."""
        layout = QVBoxLayout(self)
        
        # --- Layout Tombol ---
        # Tombol Edit dan Hapus sudah dihilangkan dari sini
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setStyleSheet("background-color: #008CBA; color: white; padding: 8px; border-radius: 4px;")
        self.refresh_btn.clicked.connect(self.load_data)
        
        # Buat layout horizontal kecil agar tombol tidak memenuhi layar
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch() # Dorong tombol ke kiri

        # --- Pengaturan Tabel ---
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # --- Mengaktifkan Context Menu (Klik Kanan) ---
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # Tambahkan layout tombol dan tabel ke layout utama
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def show_context_menu(self, position):
        """Menampilkan menu Edit/Hapus saat baris diklik kanan."""
        
        # Dapatkan item yang diklik
        item = self.table_widget.itemAt(position)
        if item is None:
            return # Pengguna mengklik area kosong, jangan lakukan apa-apa

        # Dapatkan baris dari item tersebut
        row = item.row()
        
        # Dapatkan ID pengguna dari baris itu (asumsi ID ada di kolom 0)
        try:
            user_id_item = self.table_widget.item(row, 0)
            user_id = int(user_id_item.text())
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Error mendapatkan ID dari baris {row}: {e}")
            return # Gagal mendapatkan ID

        # Buat menu
        context_menu = QMenu(self)
        
        # Buat aksi (tombol di dalam menu)
        edit_action = QAction("Edit Data Ini", self)
        delete_action = QAction("Hapus Data Ini", self)
        
        # Tambahkan aksi ke menu
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        
        # Tampilkan menu di posisi kursor global
        global_position = self.table_widget.mapToGlobal(position)
        selected_action = context_menu.exec(global_position)
        
        # --- Kirim Sinyal berdasarkan aksi yang dipilih ---
        if selected_action == edit_action:
            self.edit_requested.emit(user_id)
        elif selected_action == delete_action:
            self.delete_requested.emit(user_id)

    def load_data(self):
        """Mengambil data dari db_manager dan menampilkannya di tabel."""
        
        success, data, headers = db_manager.load_data()
        
        if success:
            if not data:
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(len(headers))
                self.table_widget.setHorizontalHeaderLabels(headers)
                return

            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(data))
            
            for row_idx, row_data in enumerate(data):
                # row_data adalah sqlite3.Row, bisa diakses by index
                for col_idx, col_value in enumerate(row_data):
                    item = QTableWidgetItem(str(col_value))
                    self.table_widget.setItem(row_idx, col_idx, item)
            
            # Sesuaikan lebar kolom 'Alamat' dan 'Keterangan' agar lebih lebar
            try:
                alamat_col = headers.index("Alamat")
                self.table_widget.horizontalHeader().setSectionResizeMode(alamat_col, QHeaderView.ResizeMode.Stretch)
                ket_col = headers.index("Keterangan")
                self.table_widget.horizontalHeader().setSectionResizeMode(ket_col, QHeaderView.ResizeMode.Stretch)
            except ValueError:
                pass # Jika kolom tidak ditemukan

        else:
            # Jika gagal, 'data' berisi pesan error
            QMessageBox.critical(self, "Error", data)