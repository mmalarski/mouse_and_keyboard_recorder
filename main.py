import argparse
from MouseRecorder import MouseRecorder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some parameters.")
    parser.add_argument(
        "--source_video", nargs="?", type=str, help="The source video file"
    )
    parser.add_argument(
        "--mouse_click_data", nargs="?", type=str, help="The mouse clicks file"
    )
    parser.add_argument(
        "--output", type=str, default="stamped_again.avi", help="The output video file"
    )

    args = parser.parse_args()

    recorder = MouseRecorder()

    if args.source_video and args.mouse_click_data:
        recorder.stamp_circles_on_raw_recording(
            args.source_video, args.output, args.mouse_click_data
        )
    else:
        recorder.setup()
        recorder.record()
        recorder.cleanup()
