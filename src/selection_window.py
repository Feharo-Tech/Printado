import sys
import time
import mss
from PyQt5.QtWidgets import QApplication, QWidget, QRubberBand, QLabel
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QScreen
from PIL import Image

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

        self.size_label = QLabel(self)
        self.size_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 4px;
            border-radius: 4px;
            font-size: 12px;
        """)
        self.size_label.hide()

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

        self.size_label.setText("0 x 0 px")
        self.size_label.move(self.origin.x() - 0, self.origin.y() - 25)
        self.size_label.show()

    def mouseMoveEvent(self, event):
        current_pos = event.globalPos()

        width = abs(current_pos.x() - self.origin.x())
        height = abs(current_pos.y() - self.origin.y())

        selection_rect = QRect(
            QPoint(min(self.origin.x(), current_pos.x()), min(self.origin.y(), current_pos.y())),
            QPoint(max(self.origin.x(), current_pos.x()), max(self.origin.y(), current_pos.y()))
        )
        self.rubberBand.setGeometry(selection_rect)

        label_text = f"{width} x {height} px"
        self.size_label.setText(label_text)
        self.size_label.adjustSize()

        label_width = self.size_label.width()
        label_height = self.size_label.height()

        options = [
            (selection_rect.left() + 10, selection_rect.top() - label_height - 10),
            (selection_rect.left() + 10, selection_rect.bottom() + 10),
            (selection_rect.left() - label_width - 10, selection_rect.top() + 10),
            (selection_rect.right() + 10, selection_rect.top() + 10)
        ]


        for x, y in options:
            if (0 <= x <= self.screen_rect.width() - label_width and
                0 <= y <= self.screen_rect.height() - label_height):
                label_x, label_y = x, y
                break
        else:
            label_x = max(0, min(current_pos.x(), self.screen_rect.width() - label_width))
            label_y = max(0, min(current_pos.y(), self.screen_rect.height() - label_height))

        self.size_label.move(label_x, label_y)


    def mouseReleaseEvent(self, event):
        self.hide()
        time.sleep(0.2)
        rect = self.rubberBand.geometry()

        with mss.mss() as sct:
            if rect.width() > 10 and rect.height() > 10:
                raw_screenshot = sct.grab({
                    "left": max(0, rect.x()), 
                    "top": max(0, rect.y()),
                    "width": rect.width(),
                    "height": rect.height()
                })
                screenshot = Image.frombytes("RGB", raw_screenshot.size, raw_screenshot.rgb)
            else:
                monitor_full = sct.monitors[0]
                raw_screenshot = sct.grab(monitor_full)
                screenshot = Image.frombytes("RGB", raw_screenshot.size, raw_screenshot.rgb)

        self.main_app.process_screenshot(screenshot)
        self.close()