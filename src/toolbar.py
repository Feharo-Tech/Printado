from PIL import ImageStat
import qtawesome as qta
from PyQt5.QtWidgets import QPushButton

def is_background_dark(image):
    grayscale_image = image.convert("L")
    stat = ImageStat.Stat(grayscale_image)
    brightness = stat.mean[0]

    return brightness < 128


def update_button_styles(toolbar_widget, is_dark, buttons):
    button_color = "black" if is_dark else "white"
    button_bg = "255, 255, 255" if is_dark else "0, 0, 0"

    toolbar_widget.setStyleSheet(
        f"background: rgba({button_bg}, 0.1); border-radius: 8px; padding: 5px;"
    )

    button_icons = {
        "enable_text_mode": "fa5s.i-cursor",
        "select_font": "fa5s.font",
        "undo_last_action": "fa5s.undo",
        "save_screenshot": "fa5s.save",
        "quit": "fa5s.trash",
    }

    for key, btn in buttons.items():
        if key in button_icons:
            new_icon = qta.icon(button_icons[key], color=button_color)
            btn.setIcon(new_icon)

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
        "enable_text_mode": ("fa5s.i-cursor", parent.enable_text_mode),
        "select_font": ("fa5s.font", parent.select_font),
        "select_color": (None, parent.select_color),
        "undo_last_action": ("fa5s.undo", parent.undo_last_action),
        "save_screenshot": ("fa5s.save", parent.save_screenshot),
        "quit": ("fa5s.trash", parent.close),
    }

    for key, (icon, action) in button_data.items():
        btn = QPushButton(qta.icon(icon), "") if icon else QPushButton()
        btn.clicked.connect(action)
        parent.toolbar.addWidget(btn)
        
        buttons[key] = btn
        
        if key == "select_color":
            parent.color_button = btn
            parent.update_color_button()

    return buttons