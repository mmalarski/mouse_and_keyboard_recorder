class CircleOverlay:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.frame_count = 0
        self.elapsed_time = 0

    def __str__(self):
        return f"Click at {self.elapsed_time} on frame {self.frame_count} at ({self.x}, {self.y})"
