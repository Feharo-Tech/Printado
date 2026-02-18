from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QColor, QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt

from printado.core.event_handler import handle_mouse_press, handle_mouse_release
from printado.core.image_utils import pil_image_to_png_bytes
from printado.core.screenshot_editor import update_screenshot as update_screenshot_core
from printado.core.screenshot_manager import process_screenshot as process_screenshot_core
from printado.core.selection_window import SelectionWindow
from printado.core.tool_manager import enable_tool
from printado.core.toolbar import setup_toolbar_buttons
from printado.core.utils import delete_temp_screenshot
from printado.modules.text_format import TextFormat
from printado.modules.upload_dialog import UploadDialog


class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.blur_background = None
        self.setWindowTitle("Printado")

        # Base image (original capture) and rendered image (base + elements)
        self.base_screenshot = None
        self.rendered_screenshot = None

        # Elements are stored in base-image coordinates
        self.elements = []
        self.history = []  # stack of previous elements snapshots

        self.selected_color = QColor(Qt.red)
        self.text_format = TextFormat()
        self.text_format.set_color(self.selected_color)

        # tool flags
        self.text_mode = False
        self.font_mode = False
        self.color_mode = False
        self.arrow_mode = False
        self.line_mode = False
        self.rectangle_mode = False
        self.size_mode = False

        self.tool_size = 5

        # runtime interaction state (display coordinates)
        self.text_position = None
        self.text_edit = None
        self.arrow_start = None
        self.arrow_end = None
        self.line_start = None
        self.line_end = None
        self.rectangle_start = None
        self.rectangle_end = None

        self.initUI()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.start_selection()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.toolbar_widget = QWidget()
        self.toolbar_widget.setStyleSheet("background: transparent; border: none;")
        self.toolbar = QVBoxLayout(self.toolbar_widget)
        self.toolbar.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        self.buttons = setup_toolbar_buttons(self)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.toolbar_widget)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def start_selection(self):
        self.selector = SelectionWindow(self)
        self.selector.selection_finished.connect(self.on_selection_finished)
        self.selector.showFullScreen()
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

    def on_selection_finished(self, screenshot):
        process_screenshot_core(self, screenshot)
        self.update_screenshot()

    def update_screenshot(self):
        update_screenshot_core(self)

    def _push_history(self):
        self.history.append(list(self.elements))

    def _display_to_base(self, x, y):
        # new_width/new_height are the displayed dimensions; original_width/original_height are base dims
        scale_x = self.original_width / max(1, self.new_width)
        scale_y = self.original_height / max(1, self.new_height)
        return int(x * scale_x), int(y * scale_y)

    def enable_text_mode(self):
        enable_tool(self, "add_text")

    def enable_font_selection(self):
        enable_tool(self, "select_font")

        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("")

        font, ok = QFontDialog.getFont(self.text_format.get_font(), self)
        if ok:
            self.text_format.set_font_family(font.family())
            self.text_format.set_font_size(font.pointSize())
            self.text_format.set_bold(font.bold())
            self.text_format.set_italic(font.italic())
            self.text_format.set_underline(font.underline())

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

    def enable_color_selection(self):
        enable_tool(self, "select_color")
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_format.set_color(color)
            self.selected_color = color
            self.update_color_button()

    def update_color_button(self):
        pixmap = QPixmap(20, 20)
        pixmap.fill(self.selected_color)
        self.color_button.setIcon(QIcon(pixmap))

    def enable_arrow_mode(self):
        enable_tool(self, "add_arrow")

    def enable_line_mode(self):
        enable_tool(self, "add_line")

    def enable_rectangle_mode(self):
        enable_tool(self, "add_rectangle")

    def enable_size_adjustment(self):
        enable_tool(self, "adjust_size")
        if not hasattr(self, "size_slider"):
            self.size_slider = QSlider(Qt.Horizontal, self)
            self.size_slider.setMinimum(1)
            self.size_slider.setMaximum(15)
            self.size_slider.setValue(self.tool_size)
            self.size_slider.setGeometry(50, 50, 200, 50)
            self.size_slider.valueChanged.connect(self.update_size)

        self.size_slider.show()

    def update_size(self, value):
        self.tool_size = int(value)

    def mousePressEvent(self, event):
        handle_mouse_press(self, event)

    def mouseReleaseEvent(self, event):
        handle_mouse_release(self, event)

    def show_text_input(self):
        if self.text_edit is not None:
            self.text_edit.deleteLater()

        self.text_edit = QLineEdit(self)
        x, y = self.text_position

        final_x = self.image_offset_x + x
        final_y = self.image_offset_y + y

        self.text_edit.setGeometry(final_x, final_y, 200, 30)
        self.text_edit.setPlaceholderText("Digite o texto aqui...")

        self.text_edit.returnPressed.connect(self.add_text_to_screenshot)
        self.text_edit.show()
        self.text_edit.raise_()
        self.text_edit.setFocus()
        self.update()

    def add_text_to_screenshot(self):
        if not self.base_screenshot or not self.text_edit:
            return

        text_input = self.text_edit.text()
        if not text_input:
            self.text_edit.deleteLater()
            self.text_edit = None
            return

        base_x, base_y = self._display_to_base(self.text_position[0], self.text_position[1])

        self._push_history()
        self.elements.append(
            (
                "text",
                text_input,
                (base_x, base_y),
                self.text_format.get_font(),
                self.selected_color.name(),
            )
        )

        self.update_screenshot()
        self.text_edit.deleteLater()
        self.text_edit = None

    def commit_arrow(self, start, end):
        if not self.base_screenshot or not start or not end:
            return

        x1, y1 = self._display_to_base(start[0], start[1])
        x2, y2 = self._display_to_base(end[0], end[1])

        self._push_history()
        self.elements.append(("arrow", (x1, y1, x2, y2), self.tool_size, self.selected_color.name()))
        self.update_screenshot()

    def commit_line(self, start, end):
        if not self.base_screenshot or not start or not end:
            return

        x1, y1 = self._display_to_base(start[0], start[1])
        x2, y2 = self._display_to_base(end[0], end[1])

        self._push_history()
        self.elements.append(("line", (x1, y1, x2, y2), self.tool_size, self.selected_color.name()))
        self.update_screenshot()

    def commit_rectangle(self, start, end):
        if not self.base_screenshot or not start or not end:
            return

        x1, y1 = self._display_to_base(start[0], start[1])
        x2, y2 = self._display_to_base(end[0], end[1])

        start_x = min(x1, x2)
        start_y = min(y1, y2)
        end_x = max(x1, x2)
        end_y = max(y1, y2)

        self._push_history()
        self.elements.append(
            ("rectangle", (start_x, start_y, end_x, end_y), self.tool_size, self.selected_color.name())
        )
        self.update_screenshot()

    def undo_last_action(self):
        if not self.history:
            return
        self.elements = self.history.pop()
        self.update_screenshot()

    def upload_screenshot(self):
        if not self.rendered_screenshot:
            return

        image_bytes = pil_image_to_png_bytes(self.rendered_screenshot)
        self.upload_dialog = UploadDialog(self)
        self.upload_dialog.start_upload(image_bytes=image_bytes, filename="printado.png")
        self.upload_dialog.exec_()

    def save_screenshot(self):
        enable_tool(self, "save_screenshot")
        if not self.rendered_screenshot:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Imagem",
            "screenshot.png",
            "PNG Files (*.png);;JPEG Files (*.jpg)",
        )
        if not filename:
            return

        self.rendered_screenshot.save(filename)
        delete_temp_screenshot()
        self.close()

    def closeEvent(self, event):
        delete_temp_screenshot()
        try:
            if self.blur_background:
                self.blur_background.hide_blur()
        except Exception:
            pass
        super().closeEvent(event)
