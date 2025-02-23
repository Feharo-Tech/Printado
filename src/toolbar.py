from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
import qtawesome as qta
from PIL import ImageStat

def is_background_dark(image):
    grayscale_image = image.convert("L")
    stat = ImageStat.Stat(grayscale_image)
    brightness = stat.mean[0]
    return brightness < 128

def set_active_tool(parent, tool_name):

    tools = {
        "enable_text_mode": "text_mode",
        "select_font": "font_mode",
        "select_color": "color_mode",
        "add_arrow": "arrow_mode",
        "add_line": "line_mode",
        "add_rectangle": "rectangle_mode",
        "adjust_size": "size_mode",
        "save_screenshot": "save_mode",
    }

    for key in tools.values():
        setattr(parent, key, False)

    if tool_name in tools:
        setattr(parent, tools[tool_name], True)

    if tool_name in ["add_arrow", "add_line", "add_rectangle"]:
        parent.setCursor(Qt.CrossCursor)
    else:
        parent.setCursor(Qt.ArrowCursor)

    if tool_name != "adjust_size":
        if hasattr(parent, 'size_slider'):
            parent.size_slider.hide()

    update_button_styles(parent.toolbar_widget, is_background_dark(parent.original_screenshot) if parent.screenshot else True, parent.buttons, tool_name)


def update_button_styles(toolbar_widget, is_dark, buttons, active_tool=None):
    button_color = "black" if is_dark else "white"
    button_bg = "255, 255, 255" if is_dark else "0, 0, 0"

    toolbar_widget.setStyleSheet(
        f"background: rgba({button_bg}, 0.1); border-radius: 8px; margin-left:3px; padding: 5px;"
    )

    button_icons = {
        "enable_text_mode": "fa5s.i-cursor",
        "select_font": "fa5s.font",
        "add_arrow": "fa5s.long-arrow-alt-right",
        "add_line": "fa5s.minus",
        "add_rectangle": "fa5s.border-style",
        "adjust_size": "fa5s.arrows-alt-v",
        "undo_last_action": "fa5s.undo",
        "save_screenshot": "fa5s.save",
        "quit": "fa5s.times",
    }

    for key, btn in buttons.items():
        if key in button_icons:
            new_icon = qta.icon(button_icons[key], color=button_color)
            btn.setIcon(new_icon)

        if key == active_tool:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({button_bg}, 0.4);
                    color: {button_color};
                    border: 1px solid rgba({button_bg}, 0.5);
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({button_bg}, 0.7);
                    color: {button_color};
                    border: 1px solid rgba({button_bg}, 0.5);
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({button_bg}, 0.4);
                }}
                QPushButton:pressed {{
                    background-color: rgba({button_bg}, 0.6);
                }}
            """)

def setup_toolbar_buttons(parent):
    buttons = {}

    button_data = {
        "enable_text_mode": ("fa5s.i-cursor", lambda: set_active_tool(parent, "enable_text_mode"), "Modo Texto"),
        "select_font": ("fa5s.font", parent.select_font, "Selecionar Fonte"),
        "select_color": (None, parent.select_color, "Selecionar Cor"),
        "add_arrow": ("fa5s.long-arrow-alt-right", lambda: set_active_tool(parent, "add_arrow"), "Adicionar Seta"),
        "add_line": ("fa5s.minus", lambda: set_active_tool(parent, "add_line"), "Adicionar Linha"),
        "add_rectangle": ("fa5s.square", lambda: set_active_tool(parent, "add_rectangle"), "Adicionar Retângulo"),
        "adjust_size": ("fa5s.arrows-alt-v", parent.open_size_slider, "Ajustar Tamanho/Espessura"),
        "undo_last_action": ("fa5s.undo", parent.undo_last_action, "Desfazer"),
        "save_screenshot": ("fa5s.save", parent.save_screenshot, "Salvar Captura"),
        "quit": ("fa5s.times", parent.close, "Descartar"),
    }

    for key, (icon, action, tooltip) in button_data.items():
        btn = QPushButton(qta.icon(icon), "") if icon else QPushButton()
        btn.clicked.connect(action)
        parent.toolbar.addWidget(btn)
        btn.setToolTip(tooltip)

        buttons[key] = btn

        if key == "select_color":
            parent.color_button = btn
            parent.update_color_button()

    parent.buttons = buttons
    apply_tooltip_style(parent)

    return buttons


def apply_tooltip_style(parent):
    is_dark = is_background_dark(parent.original_screenshot) if parent.screenshot else True

    tooltip_color = "white" if is_dark else "black"

    tooltip_style = f"""
        QToolTip {{
            color: {tooltip_color};
        }}
    """

    parent.setStyleSheet(tooltip_style)