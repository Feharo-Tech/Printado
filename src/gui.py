import os
import re
import time
import qtawesome as qta

from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QLineEdit, QColorDialog, QApplication, QFontDialog
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt

from PIL import ImageGrab, ImageDraw, ImageFont, ImageFilter
from .selection_window import SelectionWindow
from .text_format import TextFormat

class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Printado")
        self.screenshot = None
        self.texts = [] 
        self.history = []
        self.selected_color = QColor(Qt.black)
        self.text_mode = False
        self.text_position = None
        self.text_edit = None
        self.text_format = TextFormat()

        self.original_width = 0
        self.original_height = 0
        self.new_width = 0
        self.new_height = 0

        self.initUI()
        self.start_selection()
    
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) 
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;") 

        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.toolbar_widget = QWidget()
        self.toolbar_widget.setStyleSheet("background: transparent; border: none;")
        self.toolbar = QVBoxLayout(self.toolbar_widget)
        self.toolbar.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        self.text_button = QPushButton(qta.icon("fa.i-cursor"), "")
        self.text_button.clicked.connect(self.enable_text_mode)
        self.toolbar.addWidget(self.text_button)

        self.font_button = QPushButton(qta.icon("fa.font"), "")
        self.font_button.clicked.connect(self.select_font)
        self.toolbar.addWidget(self.font_button)

        self.color_button = QPushButton()
        self.update_color_button()
        self.color_button.clicked.connect(self.select_color)
        self.toolbar.addWidget(self.color_button)

        self.undo_button = QPushButton(qta.icon("fa.undo"), "")
        self.undo_button.clicked.connect(self.undo_last_action)
        self.toolbar.addWidget(self.undo_button)

        self.save_button = QPushButton(qta.icon("fa.save"), "")
        self.save_button.clicked.connect(self.save_screenshot)
        self.toolbar.addWidget(self.save_button)

        self.close_button = QPushButton(qta.icon("fa.trash"), "")
        self.close_button.clicked.connect(QApplication.quit)
        self.toolbar.addWidget(self.close_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout) 
        main_layout.addWidget(self.toolbar_widget)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setLayout(main_layout)
        self.setCentralWidget(container)


    
    def start_selection(self):
        self.selector = SelectionWindow(self)
        self.selector.showFullScreen()
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        

    def process_screenshot(self, screenshot):
        QApplication.restoreOverrideCursor()
        self.screenshot = screenshot
        self.original_screenshot = screenshot.copy()

        self.original_width, self.original_height = self.screenshot.size

        max_width = 1024
        max_height = 576

        aspect_ratio = self.original_width / self.original_height
        if self.original_width > max_width or self.original_height > max_height:
            if aspect_ratio > (max_width / max_height):
                self.new_width = max_width
                self.new_height = int(max_width / aspect_ratio)
            else:
                self.new_height = max_height
                self.new_width = int(max_height * aspect_ratio)
            
            self.screenshot = self.screenshot.resize((self.new_width, self.new_height))
            self.original_screenshot = self.original_screenshot.resize((self.new_width, self.new_height))

        else:
            self.new_width = self.original_width
            self.new_height = self.original_height

        self.screenshot.save("temp_screenshot.png")

        pixmap = QPixmap("temp_screenshot.png")
        self.label.setPixmap(pixmap)

        self.setFixedSize(self.new_width, self.new_height)

        screen_geometry = QApplication.primaryScreen().geometry()
        center_x = (screen_geometry.width() - self.new_width) // 2
        center_y = (screen_geometry.height() - self.new_height) // 2
        self.move(center_x, center_y)

        self.show()
        self.raise_()
        self.activateWindow()


    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def update_screenshot(self):
        if self.screenshot:
            self.screenshot = self.original_screenshot.copy()
            edited_screenshot = self.screenshot.copy()
            draw = ImageDraw.Draw(edited_screenshot)

            for text_data in self.texts:
                if len(text_data) == 3:
                    text, pos, color = text_data
                    font = self.text_format.get_font() 
                else:
                    text, pos, font, color = text_data

                if isinstance(color, QColor):  
                    color = color.name() 

                if isinstance(color, str) and re.match(r"^#[0-9A-Fa-f]{6}$", color):
                    color = self.hex_to_rgb(color)

                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 
                bold_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                italic_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"

                try:
                    if font.bold() and font.italic():
                        pil_font = ImageFont.truetype(bold_font_path, font.pointSize())
                    elif font.bold():
                        pil_font = ImageFont.truetype(bold_font_path, font.pointSize())
                    elif font.italic():
                        pil_font = ImageFont.truetype(italic_font_path, font.pointSize())
                    else:
                        pil_font = ImageFont.truetype(font_path, font.pointSize())
                except IOError:
                    pil_font = ImageFont.load_default() 

                draw.text(pos, text, font=pil_font, fill=color)

                if font.underline():
                    underline_y = pos[1] + font.pointSize() + 2
                    draw.line((pos[0], underline_y, pos[0] + len(text) * font.pointSize() // 2, underline_y), fill=color, width=2)

            edited_screenshot.save("temp_screenshot.png")
            pixmap = QPixmap("temp_screenshot.png")
            self.label.setPixmap(pixmap)
            self.screenshot = edited_screenshot
    
    def enable_text_mode(self):
        if self.screenshot is None:
            return  
        self.text_mode = True

    def select_font(self):
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("")

        font, ok = QFontDialog.getFont(self.text_format.get_font(), self)
        if ok:
            self.text_format.set_font_family(font.family())
            self.text_format.set_font_size(font.pointSize())
            self.text_format.set_bold(font.bold())  
            self.text_format.set_italic(font.italic())  
            self.text_format.set_underline(font.underline()) 

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_format.set_color(color.name()) 
            self.selected_color = color
            self.update_color_button()
    
    def update_color_button(self):
        pixmap = QPixmap(20, 20)
        pixmap.fill(self.selected_color)
        self.color_button.setIcon(QIcon(pixmap))
    
    def mousePressEvent(self, event):
        if self.text_mode and self.screenshot is not None:
            if self.new_width == 0 or self.new_height == 0:
                return

            label_x = self.label.pos().x()
            label_y = self.label.pos().y()

            adjusted_x = event.x() - label_x
            adjusted_y = event.y() - label_y

            adjusted_x = max(0, min(adjusted_x, self.new_width))
            adjusted_y = max(0, min(adjusted_y, self.new_height))

            self.text_position = (adjusted_x, adjusted_y)

            self.show_text_input()
            self.text_mode = False
    
    def show_text_input(self):
        if self.text_edit is not None:
            self.text_edit.deleteLater()
        self.text_edit = QLineEdit(self)

        x, y = self.text_position

        self.text_edit.setGeometry(x, y, 200, 30)
        self.text_edit.setPlaceholderText("Digite seu texto aqui...")

        self.text_edit.returnPressed.connect(self.add_text_to_screenshot)
        self.text_edit.show()
        self.text_edit.raise_()
        self.text_edit.setFocus()

        self.update()


    
    def add_text_to_screenshot(self):
      if self.screenshot and self.text_edit:
            self.text_input = self.text_edit.text()
            self.history.append((self.original_screenshot.copy(), list(self.texts)))

            font = self.text_format.get_font()
            color = self.text_format.color

            updated_texts = []
            for text_data in self.texts:
                if len(text_data) == 3: 
                    text, pos, color = text_data
                    updated_texts.append((text, pos, font, color))
                else:
                    updated_texts.append(text_data)

            self.texts = updated_texts
            self.texts.append((self.text_input, self.text_position, font, color))
            self.update_screenshot()

            self.text_edit.deleteLater()
            self.text_edit = None
    
    def undo_last_action(self):
        if self.history:  
            self.screenshot, self.texts = self.history.pop()
            self.update_screenshot()
    
    def save_screenshot(self):
        if self.screenshot:
            filename, _ = QFileDialog.getSaveFileName(None, "Salvar Imagem", "screenshot.png", "PNG Files (*.png);;JPEG Files (*.jpg)")
            if filename:
                self.screenshot.save(filename)
                QApplication.quit()
