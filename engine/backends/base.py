from abc import ABC, abstractmethod

import numpy as np


class Backend(ABC):
    @abstractmethod
    def blend(
        self,
        accumulator: np.ndarray,
        frame: np.ndarray,
        method: str,
        frame_index: int,
        total_frames: int,
    ) -> np.ndarray:
        raise NotImplementedError
