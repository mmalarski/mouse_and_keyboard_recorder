from MouseRecorder import MouseRecorder

if __name__ == "__main__":
    recorder = MouseRecorder()
    recorder.setup()
    recorder.record()
    recorder.cleanup()
