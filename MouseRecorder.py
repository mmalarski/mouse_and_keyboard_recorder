import os
import pyautogui
import cv2
import numpy as np
import mouse
import csv
import threading
import datetime

from CircleOverlay import CircleOverlay
from Timer import Timer
from ProgressBar import ProgressBar

BACKSPACE_KEY = 8
CIRCLE_RADIUS = 20
ALPHA = 0.4
FPS = 10


class MouseRecorder:
    def __init__(self):
        self.timer: Timer = Timer()
        self.progress_bar: ProgressBar = None
        self.video_writer = None
        self.clicks_to_stamp = []
        self.circles_currently_drawn: CircleOverlay = []

        self.directory = None
        self.filename_mouse_click = None
        self.filename_recording = None
        self.filename_final_recording = None

        self.file_mouse = None

        self.stop_thread_event = threading.Event()

    def record(self):
        self.timer.start()
        while not self.stop_thread_event.is_set():
            self.timer.increment_frame_counter()

            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.video_writer.write(frame)

        print(f"Recording duration: {self.timer.get_total_time()}s")

    def reset(self):
        self.clicks_to_stamp = []
        self.circles_currently_drawn = []
        self.video_writer = None

    def finalize(self):
        self.file_mouse.close()
        self.video_writer.release()
        self.video_writer = None
        mouse.unhook_all()
        cv2.destroyAllWindows()
        self.stamp_circles_on_raw_recording()
        if os.path.exists(self.filename_recording):
            os.remove(self.filename_recording)
        print(f"Recording {self.filename_final_recording} saved!")

    def set_paths(self, directory):
        self.directory = directory
        now = datetime.datetime.now().strftime("%H-%M-%S")
        self.filename_mouse_click = f"{self.directory}\\mouse_click_data_{now}.csv"
        self.filename_recording = f"{self.directory}\\recording_{now}.avi"
        self.filename_final_recording = f"{self.directory}\\final_recording_{now}.avi"

        self.file_mouse = open(self.filename_mouse_click, "w")
        mouse.on_click(self.save_mouse_click_data_to_file, args=("left",))
        mouse.on_right_click(self.save_mouse_click_data_to_file, args=("right",))
        self.enable_videowriter_with_output_filename_and_fps(
            self.filename_recording, FPS
        )

    def save_mouse_click_data_to_file(self, button):
        x, y = mouse.get_position()

        csv_writer = csv.writer(self.file_mouse, delimiter=",", lineterminator="\n")
        TOTAL_TIME = self.timer.get_total_time()
        FRAME_INDEX = self.timer.frame_counter

        csv_writer.writerow([TOTAL_TIME, x, y, FRAME_INDEX, button])

    def read_mouse_clicks_from_file(self):
        with open(self.filename_mouse_click, "r") as mouse_click_file:
            csv_reader = csv.reader(mouse_click_file, delimiter=",")
            for index, row in enumerate(csv_reader, start=1):
                TOTAL_TIME = row[0]
                X = row[1]
                Y = row[2]
                FRAME_INDEX = row[3]
                BUTTON = row[4]
                CLICK_COUNTER = index

                circle = CircleOverlay(
                    TOTAL_TIME, X, Y, FRAME_INDEX, CLICK_COUNTER, BUTTON
                )
                self.clicks_to_stamp.append(circle)

    def enable_videowriter_with_output_filename_and_fps(self, filename, fps):
        codec = cv2.VideoWriter_fourcc(*"mp4v")
        resolution = (1920, 1080)
        self.video_writer = cv2.VideoWriter(filename, codec, fps, resolution)

    def stamp_circles_on_raw_recording(self):
        self.read_mouse_clicks_from_file()

        raw_video_capture = cv2.VideoCapture(self.filename_recording)
        raw_video_total_frames = raw_video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.progress_bar = ProgressBar(raw_video_total_frames)
        self.enable_videowriter_with_output_filename_and_fps(
            self.filename_final_recording, self.timer.get_mean_fps()
        )

        try:
            while raw_video_capture.isOpened():
                self.progress_bar.update()
                is_next_frame, frame = raw_video_capture.read()
                if not is_next_frame:
                    break

                current_frame = raw_video_capture.get(cv2.CAP_PROP_POS_FRAMES)
                if self.should_draw_circle_this_frame(current_frame):
                    self.move_circle_to_drawn_list()

                self.draw_circles_on_frame(frame)
                self.video_writer.write(frame)
        finally:
            raw_video_capture.release()
            self.video_writer.release()
            self.progress_bar.close()

    def should_draw_circle_this_frame(self, current_frame):
        if len(self.clicks_to_stamp) == 0:
            return False
        else:
            return self.clicks_to_stamp[0].frame_index == current_frame

    def move_circle_to_drawn_list(self):
        self.circles_currently_drawn.append(self.clicks_to_stamp[0])
        self.check_and_remove_drawn_circles()
        self.clicks_to_stamp.pop(0)

    def check_and_remove_drawn_circles(self):
        if len(self.circles_currently_drawn) > 2:
            self.circles_currently_drawn.pop(0)

    def draw_circles_on_frame(self, frame):
        overlay = frame.copy()
        for circle in self.circles_currently_drawn:
            CIRCLE_COLOR = (0, 0, 255) if circle.button == "left" else (0, 100, 255)
            cv2.circle(overlay, (circle.x, circle.y), CIRCLE_RADIUS, CIRCLE_COLOR, -1)
            cv2.putText(
                overlay,
                circle.__str__(),
                (circle.x, circle.y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                3,
                cv2.LINE_AA,
            )
            cv2.putText(
                overlay,
                circle.__str__(),
                (circle.x, circle.y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
        cv2.addWeighted(overlay, ALPHA, frame, 1 - ALPHA, 0, frame)
