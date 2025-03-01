def get_theme(is_dark: bool):

    return {
        "bg_color": "rgba(30, 30, 30, 0.85)" if is_dark else "rgba(255, 255, 255, 0.85)",
        "text_color": "black" if is_dark else "white",
        "button_color": "black" if is_dark else "white",
        "button_bg": "255, 255, 255" if is_dark else "0, 0, 0",
        "tooltip_color": "white" if is_dark else "black",
    }
