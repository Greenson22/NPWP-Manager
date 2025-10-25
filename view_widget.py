# view_widget.py
# Berisi kelas QWidget untuk menampilkan data dalam tabel

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QHBoxLayout, QLineEdit # <-- Tambahkan QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction

import db_manager 

class ViewWidget(QWidget):
    """Widget untuk menampilkan data dalam tabel."""
    
    # Sinyal
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    detail_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Layout Tombol & Pencarian (DIPERBARUI) ---
        
        # 1. Buat widget
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari berdasarkan Nama atau NIK...")
        
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setStyleSheet("background-color: #008CBA; color: white; padding: 8px; border-radius: 4px;")
        
        # 2. Atur layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_input) # Tambahkan kotak pencarian
        button_layout.addWidget(self.refresh_btn) # Tambahkan tombol refresh
        button_layout.addStretch()

        # 3. Hubungkan sinyal
        self.refresh_btn.clicked.connect(self.clear_search_and_refresh)
        self.search_input.textChanged.connect(self.load_data)
        
        # --- Akhir Perubahan Layout ---

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def show_context_menu(self, position):
        """Menampilkan menu Edit/Hapus saat baris diklik kanan."""
        
        item = self.table_widget.itemAt(position)
        if item is None:
            return 

        row = item.row()
        
        try:
            user_id_item = self.table_widget.item(row, 0)
            user_id = int(user_id_item.text())
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Error mendapatkan ID dari baris {row}: {e}")
            return

        context_menu = QMenu(self)
        
        detail_action = QAction("Lihat Detail Data", self)
        edit_action = QAction("Edit Data Ini", self)
        delete_action = QAction("Hapus Data Ini", self)
        
        context_menu.addAction(detail_action)
        context_menu.addSeparator()
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        
        global_position = self.table_widget.mapToGlobal(position)
        selected_action = context_menu.exec(global_position)
        
        if selected_action == detail_action:
            self.detail_requested.emit(user_id)
        elif selected_action == edit_action:
            self.edit_requested.emit(user_id)
        elif selected_action == delete_action:
            self.delete_requested.emit(user_id)

    # --- FUNGSI BARU ---
    def clear_search_and_refresh(self):
        """Membersihkan kotak pencarian dan memuat ulang data."""
        # Hentikan sinyal sementara agar clear() tidak memicu load_data
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        
        # Panggil load_data secara manual
        self.load_data()

    # --- FUNGSI DIPERBARUI ---
    def load_data(self):
        """Mengambil data dari db_manager dan menampilkannya di tabel."""
        
        # Ambil teks pencarian dari input
        search_term = self.search_input.text()
        
        # Kirim teks pencarian ke db_manager
        success, data, headers = db_manager.load_data(search_term)
        
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
                for col_idx, col_value in enumerate(row_data):
                    item = QTableWidgetItem(str(col_value))
                    self.table_widget.setItem(row_idx, col_idx, item)
            
            try:
                self.table_widget.setColumnHidden(0, True)
            except Exception as e:
                print(f"Gagal menyembunyikan kolom ID: {e}")

            try:
                alamat_col = headers.index("Alamat")
                self.table_widget.horizontalHeader().setSectionResizeMode(alamat_col, QHeaderView.ResizeMode.Stretch)
                ket_col = headers.index("Keterangan")
                self.table_widget.horizontalHeader().setSectionResizeMode(ket_col, QHeaderView.ResizeMode.Stretch)
            except ValueError:
                pass 

        else:
            QMessageBox.critical(self, "Error", data)