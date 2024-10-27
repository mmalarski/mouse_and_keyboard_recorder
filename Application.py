import os
import datetime
import keyboard
from MouseRecorder import MouseRecorder


class Application:
    def __init__(self):
        # self.mouse_recorder = MouseRecorder()
        self.user_input = None
        keyboard.on_press_key("num 1", self.on_num_press)
        keyboard.on_press_key("num 2", self.on_num_press)
        keyboard.on_press_key("num 3", self.on_num_press)
        keyboard.on_press_key("num 4", self.on_num_press)
        keyboard.on_press_key("num 0", self.on_num_press)
        keyboard.on_press_key("backspace", self.on_num_press)

    def run(self):
        session_dir = self.setup_session_directories()
        active_task = None  # Track currently active task

        print("Welcome! Press 1, 2, 3, or 4 to start recording a task.")
        print("Press 0 to stop the current recording.")
        print("Press 'e' to exit the application.")

        while True:
            if self.user_input is None:
                continue
            elif self.user_input in ["1", "2", "3", "4"]:  # Start recording a new task
                if active_task is not None:
                    print(
                        f"Already recording Task {active_task}. Stop it first with '0'."
                    )
                else:
                    filename = self.get_filename(session_dir, self.user_input)
                    print(
                        f"Starting recording for Task {self.user_input}. Filename: {filename}"
                    )
                    active_task = self.user_input
                    # Here you would start your recording code for the selected task

            elif self.user_input == "0":  # Stop current recording
                if active_task is not None:
                    print(f"Stopping recording for Task {active_task}.")
                    active_task = None
                    self.user_input = None
                    # Here you would stop your recording code for the active task
                else:
                    print("No active recording to stop.")

            elif self.user_input == "backspace":  # Exit the application11
                if active_task is None:
                    print("Exiting application.")
                    break
                else:
                    print(
                        f"Recording is active for Task {active_task}. Stop it first with '0' before exiting."
                    )

            else:
                print(
                    f"Invalid input {self.user_input}. Please enter a task number (1-4), '0' to stop, or 'e' to exit."
                )

            self.user_input = None

    # def cleanup(self):
    # self.mouse_recorder.cleanup()

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

    def start_recording_task(self, user_input):
        self.user_input = user_input

    def stop_recording_task(self):
        self.user_input = 0
