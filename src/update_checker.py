import os
import sys
import requests
import webbrowser
from dotenv import load_dotenv
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
import qtawesome as qta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from version import __version__
from .toolbar import is_background_dark

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
UPDATE_URL = BASE_URL + "latest_version.json"

def check_for_update(parent):
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("latest_version", __version__)
            download_url = data.get("download_url", "")
            changelog = data.get("changelog", [])

            if latest_version > __version__:
                QTimer.singleShot(500, lambda: notify_update(parent, latest_version, download_url, changelog))
    except Exception:
        pass

class UpdateDialog(QDialog):
    def __init__(self, parent, latest_version, download_url, changelog):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        is_dark = is_background_dark(parent.original_screenshot) if parent.screenshot else True

        bg_color = "rgba(255, 255, 255, 0.85)" if is_dark else "rgba(30, 30, 30, 0.85)"
        text_color = "black" if is_dark else "white"
        button_color = "white" if is_dark else "black"
        button_bg = "0, 0, 0" if is_dark else "255, 255, 255"

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

        self.title_label = QLabel("🔔 Nova Atualização Disponível!")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: bold;")
        self.container_layout.addWidget(self.title_label)

        self.info_label = QLabel(f"<span style='color:{text_color};'>📌 Atual: <b>{__version__}</b> → 🚀 Nova: <b>{latest_version}</b></span>")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"color: {text_color}; font-size: 14px;")
        self.container_layout.addWidget(self.info_label)

        changelog_text = "\n".join(changelog) if changelog else "Nenhuma informação disponível."
        self.changelog_label = QLabel(f"📜 O que há de novo:\n{changelog_text}")
        self.changelog_label.setAlignment(Qt.AlignCenter)
        self.changelog_label.setWordWrap(True)
        self.changelog_label.setStyleSheet(f"color: {text_color}; font-size: 12px;")
        self.container_layout.addWidget(self.changelog_label)

        self.button_layout = QHBoxLayout()
        
        self.download_button = QPushButton(qta.icon("fa5s.download", color=button_color), " Baixar Agora")
        self.download_button.clicked.connect(lambda: webbrowser.open_new_tab(download_url))
        self.download_button.setStyleSheet(f"""
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

        self.remind_button = QPushButton(qta.icon("fa5s.bell-slash", color=button_color), " Lembrar Depois")
        self.remind_button.clicked.connect(self.close)
        self.remind_button.setStyleSheet(f"""
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

        self.button_layout.addWidget(self.download_button)
        self.button_layout.addWidget(self.remind_button)
        self.container_layout.addLayout(self.button_layout)

        self.setFixedWidth(400)


def notify_update(parent, latest_version, download_url, changelog):
    dialog = UpdateDialog(parent, latest_version, download_url, changelog)
    dialog.exec_()
