import os
import time
import pyautogui
import cv2
import numpy as np
import mouse
import keyboard
import csv

from circle_overlay import CircleOverlay

date_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
mouse_click_file = open(f"{date_time}_mouse_click_data.csv", "a")
recording_filename = f"{date_time}_recording.avi"
codec = cv2.VideoWriter_fourcc(*"XVID")
fps = 30.0
frame_counter = 0
resolution = (1920, 1080)
video_writer = cv2.VideoWriter(recording_filename, codec, fps, resolution)

start_time_in_seconds = time.time()


def save_mouse_click_data_to_file():
    global mouse_click_file
    global frame_counter
    elapsed_time_in_seconds = time.time() - start_time_in_seconds
    x, y = mouse.get_position()

    csv_writer = csv.writer(mouse_click_file, delimiter=",", lineterminator="\n")
    csv_writer.writerow([elapsed_time_in_seconds, x, y, frame_counter])


cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Live", 480, 270)

mouse.on_click(save_mouse_click_data_to_file)

previous_frame_timestamp = time.time()
cumulative_elapsed_time = 0
while True:
    current_frame_timestamp = time.time()
    elapsed_frame_timestamp = current_frame_timestamp - previous_frame_timestamp
    cumulative_elapsed_time += elapsed_frame_timestamp
    previous_frame_timestamp = current_frame_timestamp

    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # conver color from BGR to RGB

    video_writer.write(frame)
    cv2.imshow("Live", frame)
    frame_counter += 1

    if (
        cv2.waitKey(1) == 8  # 8 is the ASCII value of backspace
        or cv2.getWindowProperty("Live", cv2.WND_PROP_VISIBLE) < 1
        or keyboard.is_pressed("backspace")
    ):
        break

measured_s_per_frame = cumulative_elapsed_time / frame_counter
measured_fps = 1 / measured_s_per_frame

elapsed_time_in_seconds = time.time() - start_time_in_seconds
print(f"Recording duration: {elapsed_time_in_seconds}s")

mouse_click_file.close()
mouse.unhook_all()
video_writer.release()
cv2.destroyAllWindows()

clicks_to_stamp = []

with open(f"{date_time}_mouse_click_data.csv", "r") as mouse_click_file:
    csv_reader = csv.reader(mouse_click_file, delimiter=",")
    for row in csv_reader:
        circle = CircleOverlay(row[0], row[1], row[2], row[3])
        clicks_to_stamp.append(circle)

video_capture = cv2.VideoCapture(recording_filename)
video_writer = cv2.VideoWriter(
    f"{date_time}_final_recording.avi", codec, measured_fps, resolution
)

circles_currently_drawn = []
circles = []

while video_capture.isOpened():
    ret, frame = video_capture.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    current_frame = video_capture.get(cv2.CAP_PROP_POS_FRAMES)
    if len(clicks_to_stamp) > 0 and current_frame >= clicks_to_stamp[0].frame_index:

        circle_drawn = CircleOverlay(
            clicks_to_stamp[0].elapsed_time,
            clicks_to_stamp[0].x,
            clicks_to_stamp[0].y,
            clicks_to_stamp[0].frame_index,
        )
        circles_currently_drawn.append(circle_drawn)
        if len(circles_currently_drawn) > 2:
            circles_currently_drawn.pop(0)

        clicks_to_stamp.pop(0)

    overlay = frame.copy()
    alpha = 0.4
    for circle in circles_currently_drawn:
        cv2.circle(overlay, (circle.x, circle.y), 20, (0, 0, 255), -1)
        cv2.putText(
            overlay,
            circle.__str__(),
            (circle.x, circle.y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    video_writer.write(frame)

video_capture.release()
video_writer.release()

print("Recording saved as", f"{date_time}_final_recording.avi")
