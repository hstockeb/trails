import numpy as np

def blend(accumulator: np.ndarray, frame: np.ndarray,
          frame_index: int, **_) -> np.ndarray:
    n = frame_index + 1
    if n == 1:
        return frame.copy()
    return accumulator + (frame - accumulator) / n
