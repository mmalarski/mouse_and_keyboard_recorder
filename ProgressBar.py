from tqdm import tqdm


class ProgressBar:
    def __init__(self, total_frames):
        self.bar = tqdm(
            total=total_frames, desc="Processing frames", unit="frames", leave=True
        )

    def update(self):
        self.bar.update(1)

    def close(self):
        self.bar.close()
