from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, QWidget, QApplication
from PyQt5.QtCore import Qt
import webbrowser
import pyperclip
import qtawesome as qta
from .upload import UploadThread
from .toolbar import is_background_dark
from .utils import delete_temp_screenshot

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        is_dark = is_background_dark(parent.original_screenshot) if parent.screenshot else True

        bg_color = "rgba(30, 30, 30, 0.85)" if is_dark else "rgba(255, 255, 255, 0.85)"
        text_color = "white" if is_dark else "black"
        button_color = "black" if is_dark else "white"
        button_bg = "255, 255, 255" if is_dark else "0, 0, 0"

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.container = QWidget()
        self.container.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: 12px;
            padding: 15px;
        """)
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.layout.addWidget(self.container, alignment=Qt.AlignCenter)

        self.loading_label = QLabel("🔄 Enviando a imagem, aguarde...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {text_color}; font-size: 14px; font-weight: bold;")
        self.container_layout.addWidget(self.loading_label)

        self.button_layout = QHBoxLayout()
        self.copy_button = QPushButton(qta.icon("fa5s.clipboard", color=button_color), " Copiar Link")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({button_bg}, 0.7);
                color: {button_color};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba({button_bg}, 0.4);
            }}
        """)
        self.copy_button.hide()

        self.open_button = QPushButton(qta.icon("fa5s.link", color=button_color), " Abrir no Navegador")
        self.open_button.clicked.connect(self.open_in_browser)
        self.open_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({button_bg}, 0.7);
                color: {button_color};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba({button_bg}, 0.4);
            }}
        """)
        self.open_button.hide()

        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.open_button)
        self.container_layout.addLayout(self.button_layout)

        self.setFixedSize(320, 100)

    def start_upload(self, filepath):
        self.loading_label.setText("🔄 Enviando a imagem, aguarde...")
        self.loading_label.show()
        self.copy_button.hide()
        self.open_button.hide()

        self.upload_thread = UploadThread(filepath)
        self.upload_thread.upload_finished.connect(self.upload_complete)
        self.upload_thread.start()

        self.show()

    def upload_complete(self, url):
        self.loading_label.hide()

        if url.startswith("Erro"):
            self.loading_label.setText(f"❌ {url}")
            self.loading_label.show()
        else:
            self.uploaded_url = url
            self.copy_button.show()
            self.open_button.show()

        self.adjustSize()

    def copy_to_clipboard(self):
        pyperclip.copy(self.uploaded_url)
        self.copy_button.setText("✅ Copiado!")
        delete_temp_screenshot()
        QApplication.quit()

    def open_in_browser(self):
        webbrowser.open_new_tab(self.uploaded_url)
        delete_temp_screenshot()
        QApplication.quit()
