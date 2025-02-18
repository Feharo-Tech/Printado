import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QScreen
from PIL import ImageGrab

class SelectionWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;") 

        self.screen_rect = self.get_combined_screen_geometry()
        self.setGeometry(self.screen_rect)

        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        self.show() 

    def get_combined_screen_geometry(self):
        screens = QApplication.screens()
        x_min = min(screen.geometry().x() for screen in screens)
        y_min = min(screen.geometry().y() for screen in screens)
        x_max = max(screen.geometry().x() + screen.geometry().width() for screen in screens)
        y_max = max(screen.geometry().y() + screen.geometry().height() for screen in screens)

        return QRect(x_min, y_min, x_max - x_min, y_max - y_min)

    def mousePressEvent(self, event):
        self.origin = event.globalPos()
        self.rubberBand.setGeometry(QRect(self.origin, self.origin))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QRect(self.origin, event.globalPos()).normalized())

    def mouseReleaseEvent(self, event):
        self.hide()
        time.sleep(0.2) 
        rect = self.rubberBand.geometry()

        if rect.width() > 10 and rect.height() > 10:
            screenshot = ImageGrab.grab(bbox=(rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()))
        else:
            screenshot = ImageGrab.grab(all_screens=True) 

        self.main_app.process_screenshot(screenshot)
        self.close()
