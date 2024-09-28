import os
import time
import pyautogui
import cv2
import numpy as np
import mouse
import keyboard
import csv

import circle_overlay

date_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
mouse_click_file = open(f"{date_time}_mouse_click_data.csv", "a")
recording_filename = f"{date_time}_Recording.avi"
codec = cv2.VideoWriter_fourcc(*"XVID")
fps = 20.0
frame_counter = 0
resolution = (1920, 1080)
video_writer = cv2.VideoWriter(recording_filename, codec, fps, resolution)

start_time_in_milis = int(time.time() * 1000)


def save_mouse_click_data_to_file():
    global mouse_click_file
    global frame_counter
    elapsed_time_in_milis = int(time.time() * 1000 - start_time_in_milis)
    x, y = mouse.get_position()

    csv_writer = csv.writer(mouse_click_file, delimiter=",", lineterminator="\n")
    csv_writer.writerow([elapsed_time_in_milis, x, y, frame_counter])


cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Live", 480, 270)

mouse.on_click(save_mouse_click_data_to_file)

while True:
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


mouse_click_file.close()
mouse.unhook_all()
video_writer.release()
cv2.destroyAllWindows()


x_coordinates = []
y_coordinates = []
frame_counts = []

with open(f"{date_time}_mouse_click_data.csv", "r") as mouse_click_file:
    csv_reader = csv.reader(mouse_click_file, delimiter=",")
    for row in csv_reader:
        x_coordinates.append(int(row[1]))
        y_coordinates.append(int(row[2]))
        frame_counts.append(float(row[3]))

video_capture = cv2.VideoCapture(recording_filename)
video_writer = cv2.VideoWriter(
    f"{date_time}_Final_Recording.avi", codec, fps, resolution
)

circles = []

while video_capture.isOpened():
    ret, frame = video_capture.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    frame_count = video_capture.get(cv2.CAP_PROP_POS_FRAMES)
    if len(frame_counts) > 0 and frame_count >= frame_counts[0]:

        circles.append((x_coordinates[0], y_coordinates[0]))
        if len(circles) > 2:
            circles.pop(0)

        frame_counts.pop(0)
        x_coordinates.pop(0)
        y_coordinates.pop(0)

    overlay = frame.copy()
    alpha = 0.4  # Transparency factor
    for circle in circles:
        cv2.circle(overlay, (circle[0], circle[1]), 20, (0, 0, 255), -1)
        cv2.putText(
            overlay,
            f"Click on frame {frame_count} at ({circle[0]}, {circle[1]})",
            (circle[0], circle[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    video_writer.write(frame)

video_capture.release()
video_writer.release()
