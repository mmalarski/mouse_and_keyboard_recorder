import time
import os
import cv2


def create_directory_and_get_filenames():

    date_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    os.makedirs(f"{date_time}", exist_ok=True)

    mouse_click_file = open(f"{date_time}\\{date_time}_mouse_click_data.csv", "a")
    recording_filename = f"{date_time}\\{date_time}_recording.avi"

    return date_time, mouse_click_file, recording_filename


def create_videowriter_with_output_filename_and_fps(filename, fps):
    codec = cv2.VideoWriter_fourcc(*"XVID")
    resolution = (1920, 1080)
    return cv2.VideoWriter(filename, codec, fps, resolution)
