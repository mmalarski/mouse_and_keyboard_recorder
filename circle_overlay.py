class CircleOverlay:
    def __init__(self, elapsed_time, x, y, frame_index):
        self.elapsed_time = float(elapsed_time)
        self.x = int(x)
        self.y = int(y)
        self.frame_index = int(frame_index)

    def __str__(self):
        return f"Click at {self.elapsed_time}s on frame {self.frame_index} at ({self.x}, {self.y})"
