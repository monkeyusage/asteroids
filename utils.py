from time import time, sleep
from config import FPS


def sleep_fps(orig_time: float, frame_time: float = 1 / FPS) -> None:
    final_time = time()
    elapsed_time = final_time - orig_time
    if elapsed_time < frame_time:
        sleep(frame_time - elapsed_time)
