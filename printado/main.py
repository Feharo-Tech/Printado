import sys
from PyQt5.QtWidgets import QApplication
from printado.modules.gui import ScreenshotTool

def main():
    app = QApplication(sys.argv)
    window = ScreenshotTool()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
