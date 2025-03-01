def get_theme(is_dark: bool):

    return {
        "bg_color": "rgba(30, 30, 30, 0.85)" if is_dark else "rgba(255, 255, 255, 0.85)",
        "bg_color_reverse": "rgba(255, 255, 255, 0.85)" if is_dark else "rgba(30, 30, 30, 0.85)",
        "text_color": "black" if is_dark else "white",
        "button_color": "black" if is_dark else "white",
        "button_color_reverse": "white" if is_dark else "black",
        "button_bg": "255, 255, 255" if is_dark else "0, 0, 0",
        "button_bg_reverse": "0, 0, 0" if is_dark else "255, 255, 255",
        "tooltip_color": "white" if is_dark else "black",
    }
