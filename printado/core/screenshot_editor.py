from PIL import ImageDraw, ImageFont
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import re
import math


def update_screenshot(self):
    if not self.screenshot:
        return

    self.screenshot = self.original_screenshot.copy()
    edited_screenshot = self.screenshot.copy()
    draw = ImageDraw.Draw(edited_screenshot)

    scale_x = self.original_width / self.new_width
    scale_y = self.original_height / self.new_height

    for text_data in self.texts:
        _draw_elements(draw, text_data, scale_x, scale_y)

    edited_screenshot.save("temp_screenshot.png")
    self.original_screenshot = edited_screenshot.copy()
    self.screenshot = edited_screenshot

    pixmap = QPixmap("temp_screenshot.png")
    scaled_pixmap = pixmap.scaled(self.new_width, self.new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    self.label.setPixmap(scaled_pixmap)
    self.label.adjustSize()


def _draw_elements(draw, text_data, scale_x, scale_y):
    if text_data[0] == "arrow":
        _draw_arrow(draw, text_data, scale_x, scale_y)
    elif text_data[0] == "line":
        _draw_line(draw, text_data, scale_x, scale_y)
    elif text_data[0] == "rectangle":
        _draw_rectangle(draw, text_data, scale_x, scale_y)
    else:
        _draw_text(draw, text_data, scale_x, scale_y)

def _draw_arrow(draw, data, scale_x, scale_y):
    start_x, start_y, end_x, end_y = data[1]
    tool_size, color = data[2], data[3]

    start_x, start_y, end_x, end_y = map(lambda v: int(v * scale_x), [start_x, start_y, end_x, end_y])

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


def _draw_line(draw, data, scale_x, scale_y):
    start_x, start_y, end_x, end_y = data[1]
    tool_size, color = data[2], data[3]

    start_x, start_y, end_x, end_y = map(lambda v: int(v * scale_x), [start_x, start_y, end_x, end_y])

    draw.line((start_x, start_y, end_x, end_y), fill=color, width=max(2, tool_size))


def _draw_rectangle(draw, data, scale_x, scale_y):
    start_x, start_y, end_x, end_y = data[1]
    tool_size, color = data[2], data[3]

    start_x, start_y, end_x, end_y = map(lambda v: int(v * scale_x), [start_x, start_y, end_x, end_y])

    draw.rectangle([start_x, start_y, end_x, end_y], outline=color, width=tool_size)


def _draw_text(draw, data, scale_x, scale_y):
    text, pos, font, color = data

    if isinstance(color, QColor):  
        color = color.name()

    if isinstance(color, str) and re.match(r"^#[0-9A-Fa-f]{6}$", color):
        color = hex_to_rgb(color)

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

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))