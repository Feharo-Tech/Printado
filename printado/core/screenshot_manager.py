from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from printado.core.blur_background import BlurBackground
from printado.core.toolbar import is_background_dark, update_button_styles
from printado.modules.update_checker import check_for_update
from printado.core.image_utils import pil_image_to_qpixmap

def process_screenshot(screenshot_tool, screenshot):
    check_for_update(screenshot_tool)

    if not screenshot_tool.blur_background:
        screenshot_tool.blur_background = BlurBackground(screenshot_tool)
        screenshot_tool.blur_background.show_blur()
        screenshot_tool.blur_background.lower()

    QApplication.restoreOverrideCursor()
    screenshot_tool.base_screenshot = screenshot
    screenshot_tool.rendered_screenshot = screenshot.copy()
    screenshot_tool.elements = []

    adjust_screenshot_size(screenshot_tool)
    update_ui_with_screenshot(screenshot_tool)


def adjust_screenshot_size(screenshot_tool):
    min_width, min_height = 400, 300
    max_width, max_height = 1024, 576

    screenshot_tool.original_width, screenshot_tool.original_height = screenshot_tool.base_screenshot.size
    aspect_ratio = screenshot_tool.original_width / screenshot_tool.original_height

    if screenshot_tool.original_width > max_width or screenshot_tool.original_height > max_height:
        if aspect_ratio > (max_width / max_height):
            screenshot_tool.new_width = max_width
            screenshot_tool.new_height = int(max_width / aspect_ratio)
        else:
            screenshot_tool.new_height = max_height
            screenshot_tool.new_width = int(max_height * aspect_ratio)

        # keep base image in original size; resize is only for display
        pass
    else:
        screenshot_tool.new_width, screenshot_tool.new_height = screenshot_tool.original_width, screenshot_tool.original_height

    screenshot_tool.display_width = max(screenshot_tool.new_width, min_width)
    screenshot_tool.display_height = max(screenshot_tool.new_height, min_height)

    screenshot_tool.image_offset_x = (screenshot_tool.display_width - screenshot_tool.new_width) // 2
    screenshot_tool.image_offset_y = (screenshot_tool.display_height - screenshot_tool.new_height) // 2


def update_ui_with_screenshot(screenshot_tool):
    pixmap = pil_image_to_qpixmap(screenshot_tool.base_screenshot)
    pixmap = pixmap.scaled(
        screenshot_tool.new_width,
        screenshot_tool.new_height,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    screenshot_tool.label.setPixmap(pixmap)
    screenshot_tool.label.setFixedSize(screenshot_tool.display_width, screenshot_tool.display_height)
    screenshot_tool.label.setAlignment(Qt.AlignCenter)
    screenshot_tool.label.setStyleSheet("background-color: transparent;")

    screen_geometry = QApplication.primaryScreen().geometry()
    center_x = (screen_geometry.width() - 1024) // 2
    center_y = (screen_geometry.height() - 576) // 2
    screenshot_tool.move(center_x, center_y)

    is_dark = is_background_dark(screenshot_tool.base_screenshot)
    update_button_styles(screenshot_tool.toolbar_widget, is_dark, screenshot_tool.buttons)

    screenshot_tool.show()
    screenshot_tool.raise_()
    screenshot_tool.activateWindow()
