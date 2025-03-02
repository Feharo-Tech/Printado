def handle_mouse_press(self, event):
    adjusted_x = event.x() - self.image_offset_x
    adjusted_y = event.y() - self.image_offset_y
    adjusted_x = max(0, min(adjusted_x, self.new_width))
    adjusted_y = max(0, min(adjusted_y, self.new_height))

    if self.rectangle_mode:
        self.rectangle_start = (adjusted_x, adjusted_y)

    elif self.line_mode:
        self.line_start = (adjusted_x, adjusted_y)

    elif self.arrow_mode:
        self.arrow_start = (adjusted_x, adjusted_y)

    elif self.text_mode:
        self.text_position = (adjusted_x, adjusted_y)
        self.show_text_input()

def handle_mouse_release(self, event):
    adjusted_x = event.x() - self.image_offset_x
    adjusted_y = event.y() - self.image_offset_y
    adjusted_x = max(0, min(adjusted_x, self.new_width))
    adjusted_y = max(0, min(adjusted_y, self.new_height))

    if self.rectangle_mode and self.rectangle_start:
        self.rectangle_end = (adjusted_x, adjusted_y)
        self.enable_rectangle_mode()
        self.rectangle_start = None
        self.rectangle_end = None

    elif self.line_mode and self.line_start:
        self.line_end = (adjusted_x, adjusted_y)
        self.enable_line_mode()
        self.line_start = None
        self.line_end = None

    elif self.arrow_mode and self.arrow_start:
        self.arrow_end = (adjusted_x, adjusted_y)
        self.add_arrow_to_screenshot()
        self.arrow_start = None
        self.arrow_end = None
