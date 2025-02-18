from PyQt5.QtGui import QFont, QColor

class TextFormat:
    def __init__(self, font_family="Arial", font_size=18, bold=False, italic=False, underline=False, color=QColor(0, 0, 0)):
        self.font_family = font_family
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color = color

    def get_font(self):
        font = QFont(self.font_family, self.font_size)
        font.setBold(self.bold)
        font.setItalic(self.italic)
        font.setUnderline(self.underline)
        return font

    def set_font_family(self, family):
        self.font_family = family

    def set_font_size(self, size):
        self.font_size = size

    def set_bold(self, bold):
        self.bold = bold

    def set_italic(self, italic):
        self.italic = italic

    def set_underline(self, underline):
        self.underline = underline

    def set_color(self, color):
        self.color = color
