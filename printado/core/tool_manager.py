from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from printado.core.toolbar import set_active_tool

TOOL_MODES = {
    "add_text": "text_mode",
    "add_arrow": "arrow_mode",
    "add_line": "line_mode",
    "add_rectangle": "rectangle_mode",
    "select_color": "color_mode",
    "select_font": "font_mode",
    "adjust_size": "size_mode"
}

def enable_tool(parent, tool_name):
    set_active_tool(parent, tool_name)

    for mode in TOOL_MODES.values():
        setattr(parent, mode, False)

    if tool_name in TOOL_MODES:
        setattr(parent, TOOL_MODES[tool_name], True)

    if tool_name in ["add_arrow", "add_line", "add_rectangle"]:
        parent.setCursor(QCursor(Qt.CrossCursor))
    else:
        parent.setCursor(QCursor(Qt.ArrowCursor))
