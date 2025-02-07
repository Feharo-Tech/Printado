import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QRubberBand, QLineEdit, QHBoxLayout, QColorDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QScreen, QIcon, QColor
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PIL import ImageGrab, ImageDraw, ImageFont
from PyQt5.QtGui import QFontDatabase

class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Printado - Captura de Tela")
        self.setGeometry(100, 100, 800, 600)
        self.screenshot = None
        self.text_mode = False
        self.text_position = None
        self.text_input = ""
        self.text_edit = None
        self.texts = []  # Lista para armazenar textos adicionados
        self.history = []  # Histórico de modificações para desfazer ações
        self.selected_color = QColor(Qt.black)  # Cor padrão
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Captura de tela aparecerá aqui", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.toolbar = QHBoxLayout()
        self.capture_button = QPushButton("📸")
        self.capture_button.clicked.connect(self.start_selection)
        self.toolbar.addWidget(self.capture_button)
        
        self.text_button = QPushButton("📝")
        self.text_button.clicked.connect(self.enable_text_mode)
        self.toolbar.addWidget(self.text_button)
        
        self.color_button = QPushButton()
        self.update_color_button()
        self.color_button.clicked.connect(self.select_color)
        self.toolbar.addWidget(self.color_button)
        
        self.undo_button = QPushButton("↩️")
        self.undo_button.clicked.connect(self.undo_last_action)
        self.toolbar.addWidget(self.undo_button)
        
        self.save_button = QPushButton("💾")
        self.save_button.clicked.connect(self.save_screenshot)
        self.toolbar.addWidget(self.save_button)
        
        layout.addLayout(self.toolbar)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def start_selection(self):
        self.hide()
        self.selector = SelectionWindow(self)
        self.selector.showFullScreen()
    
    def capture_area(self, rect):
        self.hide()
        time.sleep(0.2)
        full_screenshot = ImageGrab.grab(all_screens=True)
        self.screenshot = full_screenshot.crop((rect.left(), rect.top(), rect.right(), rect.bottom()))
        self.texts = []  # Limpa os textos ao capturar nova imagem
        self.history.clear()  # Limpa o histórico
        self.update_screenshot()
        self.show()
    
    def update_screenshot(self):
        if self.screenshot:
            edited_screenshot = self.screenshot.copy()
            draw = ImageDraw.Draw(edited_screenshot)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            for text, pos, color in self.texts:
                draw.text(pos, text, font=font, fill=color.name())
            edited_screenshot.save("temp_screenshot.png")
            pixmap = QPixmap("temp_screenshot.png")
            self.label.setPixmap(pixmap)
            self.screenshot = edited_screenshot  # Atualiza a captura com os textos antes de salvar
    
    def enable_text_mode(self):
        if self.screenshot is None:
            return  # Impede adicionar texto antes de capturar a tela
        self.text_mode = True
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color
            self.update_color_button()
    
    def update_color_button(self):
        pixmap = QPixmap(20, 20)
        pixmap.fill(self.selected_color)
        self.color_button.setIcon(QIcon(pixmap))
    
    def mousePressEvent(self, event):
        if self.text_mode and self.screenshot is not None:
            self.text_position = (event.x(), event.y())
            self.show_text_input()
            self.text_mode = False
    
    def show_text_input(self):
        if self.text_edit is not None:
            self.text_edit.deleteLater()
        self.text_edit = QLineEdit(self)
        self.text_edit.setGeometry(self.text_position[0], self.text_position[1], 200, 30)
        self.text_edit.setPlaceholderText("Digite seu texto aqui...")
        self.text_edit.returnPressed.connect(self.add_text_to_screenshot)
        self.text_edit.show()
        self.text_edit.setFocus()
    
    def add_text_to_screenshot(self):
        if self.screenshot and self.text_edit:
            self.text_input = self.text_edit.text()
            self.history.append(list(self.texts))  # Salva o estado atual antes de modificar
            self.texts.append((self.text_input, self.text_position, self.selected_color))
            self.update_screenshot()
            self.text_edit.deleteLater()
            self.text_edit = None
    
    def undo_last_action(self):
        if self.history:
            self.texts = self.history.pop()
            self.update_screenshot()
    
    def save_screenshot(self):
        if self.screenshot:
            self.update_screenshot()  # Garante que os textos sejam aplicados antes de salvar
            filename, _ = QFileDialog.getSaveFileName(self, "Salvar Imagem", "screenshot.png", "PNG Files (*.png);;JPEG Files (*.jpg)")
            if filename:
                self.screenshot.save(filename)
                QApplication.quit()  # Finaliza o programa após salvar

class SelectionWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QSize(1, 1)))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):
        self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        rect = self.rubber_band.geometry()
        self.rubber_band.hide()
        self.close()
        self.parent.capture_area(rect)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotTool()
    window.show()
    sys.exit(app.exec_())
