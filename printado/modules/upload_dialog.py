from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, QWidget, QApplication
from PyQt5.QtCore import Qt
import webbrowser
import pyperclip
import qtawesome as qta
from printado.modules.upload import UploadThread
from printado.core.toolbar import is_background_dark
from printado.core.utils import delete_temp_screenshot
from printado.core.theme import get_theme

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        image = getattr(parent, "rendered_screenshot", None) or getattr(parent, "base_screenshot", None)
        is_dark = is_background_dark(image) if image else True
        theme = get_theme(is_dark)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.container = QWidget()
        self.container.setStyleSheet(f"""
            background-color: {theme['bg_color_reverse']};
            border-radius: 12px;
            padding: 15px;
        """)
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.layout.addWidget(self.container, alignment=Qt.AlignCenter)

        self.loading_label = QLabel("🔄 Enviando a imagem, aguarde...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {theme['text_color']}; font-size: 14px; font-weight: bold;")
        self.container_layout.addWidget(self.loading_label)

        self.button_layout = QHBoxLayout()
        self.copy_button = QPushButton(qta.icon("fa5s.clipboard", color=theme['button_color_reverse']), " Copiar Link")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({theme['button_bg_reverse']}, 0.7);
                color: {theme['button_color_reverse']};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba({theme['button_bg_reverse']}, 0.4);
            }}
        """)
        self.copy_button.hide()

        self.open_button = QPushButton(qta.icon("fa5s.link", color=theme['button_color_reverse']), " Abrir no Navegador")
        self.open_button.clicked.connect(self.open_in_browser)
        self.open_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({theme['button_bg_reverse']}, 0.7);
                color: {theme['button_color_reverse']};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba({theme['button_bg_reverse']}, 0.4);
            }}
        """)
        self.open_button.hide()

        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.open_button)
        self.container_layout.addLayout(self.button_layout)

        self.setFixedSize(320, 100)

    def start_upload(self, filepath=None, image_bytes=None, filename="screenshot.png"):
        self.loading_label.setText("🔄 Enviando a imagem, aguarde...")
        self.loading_label.show()
        self.copy_button.hide()
        self.open_button.hide()

        self.upload_thread = UploadThread(filepath=filepath, image_bytes=image_bytes, filename=filename)
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
