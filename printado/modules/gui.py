import os
import re
import time
import math
import requests
import qtawesome as qta

from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QLineEdit, QColorDialog, QApplication, QFontDialog, QSlider, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt

from PIL import ImageGrab, ImageDraw, ImageFont, ImageFilter
from printado.core.selection_window import SelectionWindow
from printado.modules.text_format import TextFormat
from printado.core.blur_background import BlurBackground
from printado.core.utils import delete_temp_screenshot
from printado.core.toolbar import is_background_dark, update_button_styles, setup_toolbar_buttons, set_active_tool
from printado.modules.upload_dialog import UploadDialog
from printado.modules.update_checker import check_for_update
from printado.core.event_handler import handle_mouse_press, handle_mouse_release
from printado.core.tool_manager import enable_tool


class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.blur_background = None
        self.setWindowTitle("Printado")
        self.screenshot = None
        self.texts = [] 
        self.history = []
        self.selected_color = QColor(Qt.red)
        self.text_mode = False
        self.text_position = None
        self.text_edit = None
        self.text_format = TextFormat()
        self.text_format.set_color(self.selected_color) 
        self.arrow_mode = False
        self.tool_size = 5
        self.arrow_start = None
        self.arrow_end = None
        self.line_mode = False
        self.line_start = None
        self.line_end = None
        self.rectangle_mode = False
        self.rectangle_start = None
        self.rectangle_end = None
        self.initUI()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
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

        self.buttons = setup_toolbar_buttons(self)

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
        check_for_update(self)
        if not self.blur_background:
            self.blur_background = BlurBackground(self)
            self.blur_background.show_blur()
            self.blur_background.lower()

        QApplication.restoreOverrideCursor()
        self.screenshot = screenshot
        self.original_screenshot = screenshot.copy()

        min_width, min_height = 400, 300
        max_width, max_height = 1024, 576

        self.original_width, self.original_height = self.screenshot.size
        aspect_ratio = self.original_width / self.original_height

        if self.original_width > max_width or self.original_height > max_height:
            if aspect_ratio > (max_width / max_height):
                self.new_width = max_width
                self.new_height = int(max_width / aspect_ratio)
            else:
                self.new_height = max_height
                self.new_width = int(max_height * aspect_ratio)
            
            self.screenshot = self.screenshot.resize((self.new_width, self.new_height))

        else:
            self.new_width, self.new_height = self.original_width, self.original_height

        self.display_width = max(self.new_width, min_width)
        self.display_height = max(self.new_height, min_height)

        self.image_offset_x = (self.display_width - self.new_width) // 2
        self.image_offset_y = (self.display_height - self.new_height) // 2

        self.screenshot.save("temp_screenshot.png")

        pixmap = QPixmap("temp_screenshot.png")
        self.label.setPixmap(pixmap)

        self.label.setFixedSize(self.display_width, self.display_height)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: transparent;")

        screen_geometry = QApplication.primaryScreen().geometry()
        center_x = (screen_geometry.width() - max_width) // 2
        center_y = (screen_geometry.height() - max_height) // 2
        self.move(center_x, center_y)

        is_dark = is_background_dark(self.original_screenshot)
        update_button_styles(self.toolbar_widget, is_dark, self.buttons)

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

            scale_x = self.original_width / self.new_width
            scale_y = self.original_height / self.new_height

            for text_data in self.texts:
                if text_data[0] == "arrow":
                    start_x, start_y, end_x, end_y = text_data[1]
                    tool_size = text_data[2]
                    color = text_data[3]
                    
                    start_x = int(start_x * scale_x)
                    start_y = int(start_y * scale_y)
                    end_x = int(end_x * scale_x)
                    end_y = int(end_y * scale_y)

                    draw.line((start_x, start_y, end_x, end_y), fill=color, width=max(2, tool_size))

                    angle = math.atan2(end_y - start_y, end_x - start_x)

                    arrow_head_size = max(8, tool_size * 4)

                    line_end_x = end_x - (arrow_head_size * 0.6) * math.cos(angle)
                    line_end_y = end_y - (arrow_head_size * 0.6) * math.sin(angle)

                    left_x = end_x - arrow_head_size * math.cos(angle - math.pi / 4)
                    left_y = end_y - arrow_head_size * math.sin(angle - math.pi / 4)
                    right_x = end_x - arrow_head_size * math.cos(angle + math.pi / 4)
                    right_y = end_y - arrow_head_size * math.sin(angle + math.pi / 4)

                    tip_x = end_x + (arrow_head_size // 6) * math.cos(angle)
                    tip_y = end_y + (arrow_head_size // 6) * math.sin(angle)

                    draw.polygon([(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], fill=color)

                elif text_data[0] == "line":
                    start_x, start_y, end_x, end_y = text_data[1]
                    line_size = text_data[2]
                    color = text_data[3]

                    start_x = int(start_x * scale_x)
                    start_y = int(start_y * scale_y)
                    end_x = int(end_x * scale_x)
                    end_y = int(end_y * scale_y)

                    draw.line((start_x, start_y, end_x, end_y), fill=color, width=max(2, line_size))

                elif text_data[0] == "rectangle":
                    start_x, start_y, end_x, end_y = text_data[1]
                    rect_size = text_data[2]
                    color = text_data[3]

                    start_x = int(start_x * scale_x)
                    start_y = int(start_y * scale_y)
                    end_x = int(end_x * scale_x)
                    end_y = int(end_y * scale_y)

                    draw.rectangle([start_x, start_y, end_x, end_y], outline=color, width=rect_size)

                else:
                    text, pos, font, color = text_data
                    if isinstance(color, QColor):  
                        color = color.name()

                    if isinstance(color, str) and re.match(r"^#[0-9A-Fa-f]{6}$", color):
                        color = self.hex_to_rgb(color)

                    adjusted_pos = (int(pos[0] * scale_x), int(pos[1] * scale_y))

                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    bold_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    italic_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"

                    try:
                        if font.bold() and font.italic():
                            pil_font = ImageFont.truetype(bold_font_path, font.pointSize() * scale_x)
                        elif font.bold():
                            pil_font = ImageFont.truetype(bold_font_path, font.pointSize() * scale_x)
                        elif font.italic():
                            pil_font = ImageFont.truetype(italic_font_path, font.pointSize() * scale_x)
                        else:
                            pil_font = ImageFont.truetype(font_path, font.pointSize() * scale_x)
                    except IOError:
                        pil_font = ImageFont.load_default()

                    draw.text(pos, text, font=pil_font, fill=color)

                    if font.underline():
                        underline_y = pos[1] + font.pointSize() + 2
                        draw.line((pos[0], underline_y, pos[0] + len(text) * font.pointSize() // 2, underline_y), fill=color, width=2)


            edited_screenshot.save("temp_screenshot.png")
            self.original_screenshot = edited_screenshot.copy()
            self.screenshot = edited_screenshot

            pixmap = QPixmap("temp_screenshot.png")
            scaled_pixmap = pixmap.scaled(self.new_width, self.new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.label.setPixmap(scaled_pixmap)
            self.label.adjustSize()
    
    def enable_text_mode(self):
        enable_tool(self, "add_text")

    def enable_font_selection(self):
        enable_tool(self, "select_font")
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
    
    def enable_color_selection(self):
        enable_tool(self, "select_color")
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
        handle_mouse_press(self, event)

    def mouseReleaseEvent(self, event):
        handle_mouse_release(self, event)
    
    def show_text_input(self):
        if self.text_edit is not None:
            self.text_edit.deleteLater()

        self.text_edit = QLineEdit(self)

        x, y = self.text_position

        final_x = self.image_offset_x + x
        final_y = self.image_offset_y + y


        self.text_edit.setGeometry(final_x, final_y, 200, 30)
        self.text_edit.setPlaceholderText("Digite seu texto aqui...")

        self.text_edit.returnPressed.connect(self.add_text_to_screenshot)
        self.text_edit.show()
        self.text_edit.raise_()
        self.text_edit.setFocus()

        self.update()
    
    def add_text_to_screenshot(self):
        if self.screenshot and self.text_edit:
            text_input = self.text_edit.text()

            scale_x = self.original_width / self.new_width
            scale_y = self.original_height / self.new_height

            label_x = (self.label.width() - self.new_width) // 2
            label_y = (self.label.height() - self.new_height) // 2

            adjusted_x = int(self.text_position[0] * scale_x)
            adjusted_y = int(self.text_position[1] * scale_y)

            self.history.append((self.original_screenshot.copy(), list(self.texts)))

            self.texts.append((text_input, (adjusted_x, adjusted_y), self.text_format.get_font(), self.text_format.color))
            self.update_screenshot()
            self.text_edit.deleteLater()
            self.text_edit = None

    def enable_arrow_mode(self):
        enable_tool(self, "add_arrow")
    
    def add_arrow_to_screenshot(self):
        if self.screenshot and self.arrow_start and self.arrow_end:

            self.history.append((self.screenshot.copy(), list(self.texts)))

            start_x, start_y = int(self.arrow_start[0]), int(self.arrow_start[1])
            end_x, end_y = int(self.arrow_end[0]), int(self.arrow_end[1])

            self.texts.append(("arrow", (start_x, start_y, end_x, end_y), self.tool_size, self.selected_color.name()))

            self.update_screenshot()

            self.arrow_start = None
            self.arrow_end = None


    def enable_size_adjustment(self):
        enable_tool(self, "adjust_size")
        if not hasattr(self, 'size_slider'):
            self.size_slider = QSlider(Qt.Horizontal, self)
            self.size_slider.setMinimum(1)
            self.size_slider.setMaximum(15)
            self.size_slider.setValue(self.tool_size)
            self.size_slider.setGeometry(50, 50, 200, 50)
            self.size_slider.valueChanged.connect(self.update_size)

        self.size_slider.show()

    def update_size(self, value):
        self.tool_size = value

    def enable_line_mode(self):
        enable_tool(self, "add_line")
        if self.screenshot and self.line_start and self.line_end:
            self.history.append((self.screenshot.copy(), list(self.texts)))

            start_x, start_y = int(self.line_start[0]), int(self.line_start[1])
            end_x, end_y = int(self.line_end[0]), int(self.line_end[1])

            self.texts.append(("line", (start_x, start_y, end_x, end_y), self.tool_size, self.selected_color.name()))

            self.update_screenshot()

            self.line_start = None
            self.line_end = None


    def enable_rectangle_mode(self):
        enable_tool(self, "add_rectangle")
        if self.screenshot and self.rectangle_start and self.rectangle_end:

            self.history.append((self.screenshot.copy(), list(self.texts)))

            start_x = min(self.rectangle_start[0], self.rectangle_end[0])
            start_y = min(self.rectangle_start[1], self.rectangle_end[1])
            end_x = max(self.rectangle_start[0], self.rectangle_end[0])
            end_y = max(self.rectangle_start[1], self.rectangle_end[1])

            self.texts.append(("rectangle", (start_x, start_y, end_x, end_y), self.tool_size, self.selected_color.name()))

            self.update_screenshot()

            
    def undo_last_action(self):
        if self.history:  
            last_screenshot, last_texts = self.history.pop()

            self.original_screenshot = last_screenshot.copy()
            self.screenshot = last_screenshot.copy()
            self.texts = list(last_texts)

            self.update_screenshot()

    def upload_screenshot(self):
        if self.screenshot:
            filename = "temp_screenshot.png"
            self.screenshot.save(filename)

            self.upload_dialog = UploadDialog(self)
            self.upload_dialog.start_upload(filename)
            self.upload_dialog.exec_()
            
    def save_screenshot(self):
        enable_tool(self, "save_screenshot")
        if self.original_screenshot:
            filename, _ = QFileDialog.getSaveFileName(None, "Salvar Imagem", "screenshot.png", "PNG Files (*.png);;JPEG Files (*.jpg)")
            if filename:
                self.original_screenshot.save(filename)
                delete_temp_screenshot()
                QApplication.quit()

