import sys
from PyQt5.QtWidgets import QApplication, QWidget, QRubberBand
from PyQt5.QtCore import QRect, QPoint, Qt, QSize

class ScreenCaptureSelector(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background: rgba(0, 0, 0, 0.3);")
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.show()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.close()
        selected_rect = self.rubberBand.geometry()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    selector = ScreenCaptureSelector()
    sys.exit(app.exec_())
