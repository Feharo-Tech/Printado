from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import ImageGrab, ImageFilter

class BlurBackground(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(self.get_fullscreen_geometry())
        self.apply_blur()
        self.show()

    def get_fullscreen_geometry(self):
        screens = QApplication.screens()
        x_min = min(screen.geometry().x() for screen in screens)
        y_min = min(screen.geometry().y() for screen in screens)
        width = max(screen.geometry().right() for screen in screens) - x_min
        height = max(screen.geometry().bottom() for screen in screens) - y_min
        return x_min, y_min, width, height

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