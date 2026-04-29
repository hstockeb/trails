import numpy as np

def blend(accumulator: np.ndarray, frame: np.ndarray, *_, **__) -> np.ndarray:
    return np.maximum(accumulator, frame)
