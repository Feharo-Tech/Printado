import sys
from PyQt5.QtWidgets import QApplication
from printado.modules.gui import ScreenshotTool

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotTool()
    sys.exit(app.exec_())
