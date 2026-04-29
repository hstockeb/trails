import numpy as np

DECAY = 0.97

def blend(accumulator: np.ndarray, frame: np.ndarray,
          decay: float = DECAY, **_) -> np.ndarray:
    return np.maximum(accumulator * decay, frame)
