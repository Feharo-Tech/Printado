import os
import sys
import threading

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon
from pynput import keyboard

from printado.modules.gui import ScreenshotTool


tray = None
menu = None
current_tool = None


def _resolve_app_icon() -> QIcon:
    icon = QIcon.fromTheme("printado")
    if not icon.isNull():
        return icon

    base_dir = os.path.dirname(__file__)
    for candidate in ("assets/printado.png", "assets/icon.png"):
        icon_path = os.path.join(base_dir, candidate)
        if os.path.exists(icon_path):
            return QIcon(icon_path)

    return QIcon()


def start_capture():
    """Open the capture tool."""
    global current_tool

    try:
        if current_tool is not None:
            current_tool.close()
    except Exception:
        pass

    current_tool = ScreenshotTool()


def create_tray(app: QApplication):
    global tray, menu

    tray = QSystemTrayIcon(_resolve_app_icon(), app)
    tray.setToolTip("Printado - Captura de tela")

    menu = QMenu()
    capture_action = QAction("Capturar tela")
    quit_action = QAction("Sair")

    capture_action.triggered.connect(start_capture)
    quit_action.triggered.connect(QCoreApplication.quit)

    menu.addAction(capture_action)
    menu.addSeparator()
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.show()


def start_hotkey_listener():
    """Global hotkey PrintScreen.

    Note: On some Ubuntu/GNOME setups, PrintScreen is reserved by the system
    screenshot shortcut. If it does not trigger, disable/rebind the system
    PrintScreen shortcut in Keyboard settings.
    """

    def listener_thread():
        def on_press(key):
            try:
                if key == keyboard.Key.print_screen:
                    QTimer.singleShot(0, start_capture)
            except Exception:
                pass

        def on_release(key):
            return

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    thread = threading.Thread(target=listener_thread, daemon=True)
    thread.start()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    create_tray(app)
    start_hotkey_listener()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
