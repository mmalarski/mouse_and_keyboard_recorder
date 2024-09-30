import time


class Timer:
    def __init__(self):
        self.frame_counter = int(0)
        self.start_timestamp = time.time()
        self.last_frame_timestamp = self.start_timestamp

    def get_time_since_start(self):
        return time.time() - self.start_timestamp

    def get_time_since_last_frame(self):
        return time.time() - self.last_frame_timestamp

    def count_frame(self):
        self.frame_counter += 1
        self.last_frame_timestamp = time.time()

    def start(self):
        self.start_timestamp = time.time()

    def get_mean_fps(self):
        return self.frame_counter / self.get_time_since_start()
