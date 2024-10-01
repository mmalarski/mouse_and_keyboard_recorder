import os
import time
import pyautogui
import cv2
import numpy as np
import mouse
import keyboard
import csv

from CircleOverlay import CircleOverlay
from Timer import Timer
from ProgressBar import ProgressBar

BACKSPACE_KEY = 8
CIRCLE_RADIUS = 20
CIRCLE_COLOR = (0, 0, 255)
ALPHA = 0.4
FPS = 30


class MouseRecorder:
    def __init__(self):
        self.timer: Timer = Timer()
        self.progress_bar: ProgressBar = None
        self.video_writer = None
        self.clicks_to_stamp = []
        self.circles_currently_drawn: CircleOverlay = []

        date_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        os.makedirs(f"{date_time}", exist_ok=True)
        self.filename_mouse_click = f"{date_time}\\mouse_click_data.csv"
        self.filename_recording = f"{date_time}\\recording.avi"
        self.filename_final_recording = f"{date_time}\\final_recording.avi"

        self.file_mouse = open(self.filename_mouse_click, "w")

    def save_mouse_click_data_to_file(self):
        x, y = mouse.get_position()

        csv_writer = csv.writer(self.file_mouse, delimiter=",", lineterminator="\n")
        csv_writer.writerow(
            [self.timer.get_time_since_start(), x, y, self.timer.frame_counter]
        )

    def enable_videowriter_with_output_filename_and_fps(self, filename, fps):
        codec = cv2.VideoWriter_fourcc(*"XVID")
        resolution = (1920, 1080)
        self.video_writer = cv2.VideoWriter(filename, codec, fps, resolution)

    def setup(self):
        mouse.on_click(self.save_mouse_click_data_to_file)
        self.enable_videowriter_with_output_filename_and_fps(
            self.filename_recording, FPS
        )

        cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Live", 480, 270)

    def record(self):
        self.timer.start()
        while True:
            self.timer.count_frame()

            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.video_writer.write(frame)
            cv2.imshow("Live", frame)

            if (
                cv2.waitKey(1) == BACKSPACE_KEY
                or cv2.getWindowProperty("Live", cv2.WND_PROP_VISIBLE) < 1
                or keyboard.is_pressed("backspace")
            ):
                break
        print(f"Recording duration: {self.timer.get_time_since_start()}s")

    def cleanup(self):
        self.file_mouse.close()
        self.video_writer.release()
        mouse.unhook_all()
        cv2.destroyAllWindows()
        self.stamp_circles_on_raw_recording()
        if os.path.exists(self.filename_recording):
            os.remove(self.filename_recording)
        print("Done!")

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

    def read_mouse_clicks_from_file(self):
        with open(self.filename_mouse_click, "r") as mouse_click_file:
            csv_reader = csv.reader(mouse_click_file, delimiter=",")
            for index, row in enumerate(csv_reader, start=1):
                circle = CircleOverlay(row[0], row[1], row[2], row[3], index)
                self.clicks_to_stamp.append(circle)

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
