import math
from PIL import ImageDraw, ImageFont
from PyQt5.QtCore import Qt

from printado.core.image_utils import pil_image_to_qpixmap


_FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
_FONT_BOLD_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"


def update_screenshot(self):
    """Re-render the screenshot from the base image + elements."""
    if not getattr(self, "base_screenshot", None):
        return

    rendered = render_image(self.base_screenshot, getattr(self, "elements", []))
    self.rendered_screenshot = rendered

    pixmap = pil_image_to_qpixmap(rendered)
    scaled_pixmap = pixmap.scaled(
        self.new_width,
        self.new_height,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )

    self.label.setPixmap(scaled_pixmap)
    self.label.adjustSize()


def render_image(base_image, elements):
    edited = base_image.copy()
    draw = ImageDraw.Draw(edited)

    for element in elements:
        kind = element[0]
        if kind == "text":
            _draw_text(draw, element)
        elif kind == "arrow":
            _draw_arrow(draw, element)
        elif kind == "line":
            _draw_line(draw, element)
        elif kind == "rectangle":
            _draw_rectangle(draw, element)

    return edited


def _pil_font_from_qfont(qfont):
    size = int(qfont.pointSize() or 18)

    if qfont.bold() and qfont.italic():
        font_path = _FONT_BOLD_ITALIC
    elif qfont.bold():
        font_path = _FONT_BOLD
    elif qfont.italic():
        font_path = _FONT_ITALIC
    else:
        font_path = _FONT_REGULAR

    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def _draw_text(draw, element):
    _, text, pos, qfont, color = element
    pil_font = _pil_font_from_qfont(qfont)
    x, y = int(pos[0]), int(pos[1])

    draw.text((x, y), text, font=pil_font, fill=color)

    if qfont.underline():
        try:
            text_width = int(draw.textlength(text, font=pil_font))
        except Exception:
            text_width = int(len(text) * max(8, pil_font.size // 2))
        underline_y = y + pil_font.size + 2
        draw.line((x, underline_y, x + text_width, underline_y), fill=color, width=2)


def _draw_line(draw, element):
    _, (x1, y1, x2, y2), size, color = element
    draw.line((int(x1), int(y1), int(x2), int(y2)), fill=color, width=max(2, int(size)))


def _draw_rectangle(draw, element):
    _, (x1, y1, x2, y2), size, color = element
    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline=color, width=max(1, int(size)))


def _draw_arrow(draw, element):
    _, (x1, y1, x2, y2), size, color = element
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    size = max(2, int(size))

    draw.line((x1, y1, x2, y2), fill=color, width=size)

    angle = math.atan2(y2 - y1, x2 - x1)
    head_size = max(10, size * 4)

    left_x = x2 - head_size * math.cos(angle - math.pi / 4)
    left_y = y2 - head_size * math.sin(angle - math.pi / 4)
    right_x = x2 - head_size * math.cos(angle + math.pi / 4)
    right_y = y2 - head_size * math.sin(angle + math.pi / 4)

    draw.polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], fill=color)
