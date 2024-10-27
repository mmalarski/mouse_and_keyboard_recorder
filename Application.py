import os
import datetime
import keyboard
from MouseRecorder import MouseRecorder


class Application:
    def __init__(self):
        # self.mouse_recorder = MouseRecorder()
        self.user_input = None
        self.active_task = None
        self.session_dir = self.setup_session_directories()
        self.exit = False
        keyboard.on_press_key("num 1", self.on_num_press)
        keyboard.on_press_key("num 2", self.on_num_press)
        keyboard.on_press_key("num 3", self.on_num_press)
        keyboard.on_press_key("num 4", self.on_num_press)
        keyboard.on_press_key("num 0", self.on_num_press)
        keyboard.on_press_key("backspace", self.on_num_press)

    def run(self):

        print("Welcome! Press numpad 1, 2, 3, or 4 to start recording a task.")
        print("Press numpad 0 to stop the current recording.")
        print("Press 'backspace' to exit the application.")

        while self.exit is False:
            self.update()

    # def cleanup(self):
    # self.mouse_recorder.cleanup()

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
                f"Invalid input {self.user_input}. Please enter a task number (numpad 1-4), '0' to stop, or 'backspace' to exit."
            )

        self.user_input = None

    def start_recording_task(self, task_num):
        if self.active_task is not None:
            print(f"Already recording Task {self.active_task}. Stop it first with '0'.")
            return
        else:
            filename = self.get_filename(self.session_dir, task_num)
            print(f"Starting recording for Task {task_num}. Filename: {filename}")
            self.active_task = task_num
            # Here you would start your recording code for the selected task

    def stop_recording_task(self):
        if self.active_task is not None:
            print(f"Stopping recording for Task {self.active_task}.")
            self.active_task = None
            self.user_input = None
            # Here you would stop your recording code for the active task
        else:
            print("No active recording to stop.")

    def terminate(self):
        if self.active_task is None:
            print("Exiting application.")
            self.exit = True
        else:
            print(
                f"Recording is active for Task {self.active_task}. Stop it first with '0' before exiting."
            )

    def on_num_press(self, num):
        self.user_input = num.name

    def setup_session_directories(self):
        # Create a main session directory named with the current datetime
        session_dir = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(session_dir, exist_ok=True)

        # Create subdirectories for each task within the session directory
        for i in range(1, 5):
            os.makedirs(os.path.join(session_dir, f"task_{i}"), exist_ok=True)

        return session_dir

    def get_filename(self, session_dir, task_num):
        # Generate a unique filename within the specific task's directory
        dt_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            session_dir, f"task_{task_num}", f"{dt_str}_task_{task_num}.avi"
        )
