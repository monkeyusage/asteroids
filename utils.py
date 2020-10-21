from time import time, sleep
from config import FPS
from typing import Union, List


def sleep_fps(orig_time: float, frame_time: float = 1 / FPS) -> None:
    final_time = time()
    elapsed_time = final_time - orig_time
    if elapsed_time < frame_time:
        sleep(frame_time - elapsed_time)

def is_point(coords) -> bool:
    if len(coords) == 2:
        return True
    return False