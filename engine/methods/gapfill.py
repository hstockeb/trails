import numpy as np
from typing import Callable

def stack(frame_paths: list[str],
          decode_fn: Callable[[str], np.ndarray],
          bright_threshold: float = 0.05) -> np.ndarray:
    """
    Two-pass gap fill.
    Pass 1 (forward): lighten blend, record last bright value and frame index per pixel.
    Pass 2 (backward): record first bright value from the end per pixel.
    Fill: pixels that were dark but have a bright anchor on both sides get interpolated.
    """
    if not frame_paths:
        raise ValueError("frame_paths is empty")

    n = len(frame_paths)
    first = decode_fn(frame_paths[0])
    h, w, c = first.shape
    shape = (h, w, c)

    trail = np.zeros(shape, dtype=np.float32)
    last_bright = np.zeros(shape, dtype=np.float32)
    last_bright_idx = np.full((h, w, c), -1, dtype=np.int32)

    # Pass 1: forward lighten + track last bright pixel per position
    for i, path in enumerate(frame_paths):
        frame = decode_fn(path) if i > 0 else first
        bright_mask = frame > bright_threshold
        trail = np.maximum(trail, frame)
        last_bright = np.where(bright_mask, frame, last_bright)
        last_bright_idx = np.where(bright_mask, i, last_bright_idx)

    # Pass 2: backward — find first bright pixel from the end per position
    first_bright_from_end = np.zeros(shape, dtype=np.float32)
    first_bright_from_end_idx = np.full((h, w, c), n, dtype=np.int32)

    for i in range(n - 1, -1, -1):
        frame = decode_fn(frame_paths[i])
        bright_mask = frame > bright_threshold
        first_bright_from_end = np.where(bright_mask, frame, first_bright_from_end)
        first_bright_from_end_idx = np.where(bright_mask, i, first_bright_from_end_idx)

    # Fill: pixels that are dark in trail but have bright anchors on both sides
    has_left = last_bright_idx >= 0
    has_right = first_bright_from_end_idx < n
    gap_exists = (trail <= bright_threshold) & has_left & has_right & (last_bright_idx < first_bright_from_end_idx)

    filled = np.where(gap_exists, (last_bright + first_bright_from_end) / 2.0, trail)
    return filled
