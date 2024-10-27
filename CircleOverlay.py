class CircleOverlay:
    def __init__(self, total_time, x, y, frame_index, click_counter, button):
        self.total_time = float(total_time)
        self.x = int(x)
        self.y = int(y)
        self.frame_index = int(frame_index)
        self.click_counter = int(click_counter)
        self.button = button

    def __str__(self):
        return f"Click {self.click_counter} {self.button} at {self.total_time:.3f}s on frame {self.frame_index} at ({self.x}, {self.y})"
