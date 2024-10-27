import os
import datetime
import threading
import keyboard
from MouseRecorder import MouseRecorder


class Application:
    def __init__(self):
        self.mouse_recorder = MouseRecorder()
        self.user_input = None
        self.active_task = None
        self.session_dir = self.setup_session_directories()

        self.should_app_exit = False

        self.recording_thread = None
        self.stop_thread_event = threading.Event()
        keyboard.add_hotkey("num 1", lambda: self.on_num_press(1))
        keyboard.add_hotkey("num 2", lambda: self.on_num_press(2))
        keyboard.add_hotkey("num 3", lambda: self.on_num_press(3))
        keyboard.add_hotkey("num 4", lambda: self.on_num_press(4))
        keyboard.add_hotkey("num 0", lambda: self.on_num_press(0))
        keyboard.add_hotkey("backspace", self.on_backspace_press)

    def run(self):

        print("Welcome! Press numpad 1, 2, 3, or 4 to start recording a task.")
        print("Press numpad 0 to stop the current recording.")
        print("Press 'backspace' to exit the application.")

        while self.should_app_exit is False:
            self.update()

    def update(self):
        if self.user_input is None:
            return
        elif self.user_input in ["1", "2", "3", "4"]:
            self.start_recording_task(self.user_input)

        elif self.user_input == "0":
            self.stop_recording_task()

        elif self.user_input == "backspace":
            self.terminate()

        else:
            print(
                f"Invalid input {self.user_input}. Please enter a task number (numpad 1-4), '0' to stop, or 'backspace' to should_app_exit."
            )

        self.user_input = None

    def start_recording_task(self, task_num):
        if self.active_task is not None:
            print(f"Already recording Task {self.active_task}. Stop it first with '0'.")
            return
        else:
            self.mouse_recorder = MouseRecorder()
            directory = self.get_directory(task_num)
            print(f"Starting recording for Task {task_num}. Filename: {directory}")
            self.active_task = task_num
            self.mouse_recorder.reset()
            self.mouse_recorder.set_paths(directory)
            self.recording_thread = threading.Thread(target=self.mouse_recorder.record)
            self.recording_thread.start()

    def stop_recording_task(self):
        if self.active_task is not None:
            print(f"Stopping recording for Task {self.active_task}.")
            self.mouse_recorder.stop_thread_event.set()
            self.recording_thread.join()
            self.active_task = None
            self.user_input = None
            self.mouse_recorder.finalize()
            self.mouse_recorder = None
        else:
            print("No active recording to stop.")

    def terminate(self):
        if self.active_task is None:
            print("Exiting application.")
            self.should_app_exit = True
        else:
            print(
                f"Recording is active for Task {self.active_task}. Stop it first with '0' before should_app_exiting."
            )

    def on_num_press(self, code):
        self.user_input = str(code)

    def on_backspace_press(self):
        self.user_input = "backspace"

    def setup_session_directories(self):
        # Create a main session directory named with the current datetime
        session_dir = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(session_dir, exist_ok=True)

        # Create subdirectories for each task within the session directory
        for i in range(1, 5):
            os.makedirs(os.path.join(session_dir, f"task_{i}"), exist_ok=True)

        return session_dir

    def get_directory(self, task_num):
        return os.path.join(self.session_dir, f"task_{task_num}")
