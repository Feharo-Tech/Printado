import os
import time
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QLineEdit, QColorDialog, QApplication
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt

from PIL import ImageGrab, ImageDraw, ImageFont, ImageFilter
from .selection_window import SelectionWindow

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

        self.undo_button = QPushButton("↩")
        self.undo_button.clicked.connect(self.undo_last_action)
        self.toolbar.addWidget(self.undo_button)

        self.save_button = QPushButton("💾")
        self.save_button.clicked.connect(self.save_screenshot)
        self.toolbar.addWidget(self.save_button)

        self.close_button = QPushButton("🗑")
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

    def process_screenshot(self, screenshot):
        self.screenshot = screenshot

        max_width = 1024
        max_height = 576

        original_width, original_height = self.screenshot.size

        aspect_ratio = original_width / original_height
        if original_width > max_width or original_height > max_height:
            if aspect_ratio > (max_width / max_height):
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            
            self.screenshot = self.screenshot.resize((new_width, new_height))
        else:
            new_width, new_height = original_width, original_height

        self.screenshot.save("temp_screenshot.png")

        pixmap = QPixmap("temp_screenshot.png")
        self.label.setPixmap(pixmap)

        self.setFixedSize(new_width, new_height)

        screen_geometry = QApplication.primaryScreen().geometry()
        center_x = (screen_geometry.width() - new_width) // 2
        center_y = (screen_geometry.height() - new_height) // 2
        self.move(center_x, center_y)

        self.show()
        self.raise_()
        self.activateWindow()

   
    def capture_area(self, rect):
        self.hide()
        time.sleep(0.2)
        full_screenshot = ImageGrab.grab(all_screens=True)
        self.screenshot = full_screenshot.crop((rect.left(), rect.top(), rect.right(), rect.bottom()))
        self.texts = [] 
        self.history.clear()
        self.update_screenshot()
        self.show()
    
    def update_screenshot(self):
        if self.screenshot:
            edited_screenshot = self.screenshot.copy()
            draw = ImageDraw.Draw(edited_screenshot)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            except IOError:
                font = ImageFont.load_default()
            for text, pos, color in self.texts:
                draw.text(pos, text, font=font, fill=color.name())
            edited_screenshot.save("temp_screenshot.png")
            pixmap = QPixmap("temp_screenshot.png")
            self.label.setPixmap(pixmap)
            self.screenshot = edited_screenshot
    
    def enable_text_mode(self):
        if self.screenshot is None:
            return  
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

          self.history.append((self.screenshot.copy(), list(self.texts)))

          self.texts.append((self.text_input, self.text_position, self.selected_color))

          self.update_screenshot()

          self.text_edit.deleteLater()
          self.text_edit = None
    
    def undo_last_action(self):
        if self.history:  
            self.screenshot, self.texts = self.history.pop()

            self.update_screenshot()
    
    def save_screenshot(self):
        if self.screenshot:
            self.update_screenshot()  

            filename, _ = QFileDialog.getSaveFileName(
                None, 
                "Salvar Imagem",
                "screenshot.png",
                "PNG Files (*.png);;JPEG Files (*.jpg)",
                options=QFileDialog.Options()
            )

            if filename:
                self.screenshot.save(filename)
                QApplication.quit() 