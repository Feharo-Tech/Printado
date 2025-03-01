from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QRect
from PIL import ImageGrab, ImageFilter

class BlurBackground(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint | Qt.BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        geometry = self.get_fullscreen_geometry()
        self.setGeometry(geometry)
        self.apply_blur()

    def show_blur(self):
        self.show()
        QApplication.processEvents()
        self.lower()
        if self.parent():
            self.stackUnder(self.parent())

    def hide_blur(self):
        self.close()

    def get_fullscreen_geometry(self):
        screens = QApplication.screens()
        x_min = min(screen.geometry().x() for screen in screens)
        y_min = min(screen.geometry().y() for screen in screens)
        width = max(screen.geometry().right() for screen in screens) - x_min
        height = max(screen.geometry().bottom() for screen in screens) - y_min
        return QRect(x_min, y_min, width, height)

    def apply_blur(self):
        screenshot = ImageGrab.grab()
        blurred_image = screenshot.filter(ImageFilter.GaussianBlur(radius=15))
        qimage = self.pil_to_qimage(blurred_image)
        pixmap = QPixmap.fromImage(qimage)
        self.setPixmap(pixmap)
        self.setScaledContents(True)

    def pil_to_qimage(self, pil_image):
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "BGRA")
        return QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)