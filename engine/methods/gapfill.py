import numpy as np
from typing import Callable

def stack(frame_paths: list[str],
          decode_fn: Callable[[str], np.ndarray],
          bright_threshold: float = 0.05) -> np.ndarray:
    """
    Two-pass gap fill. Inputs must be float32 arrays normalized to [0, 1].
    Pass 1 (forward): lighten blend, record last bright value and frame index per pixel.
    Pass 2 (backward): record first bright value from the end per pixel.
    Fill: pixels dark in both passes with bright anchors on both sides get interpolated.
    A pixel is considered "bright" if any channel exceeds bright_threshold.
    """
    if not frame_paths:
        raise ValueError("frame_paths is empty")

    n = len(frame_paths)
    first = decode_fn(frame_paths[0])
    h, w, c = first.shape
    shape = (h, w, c)

    trail = np.zeros(shape, dtype=np.float32)
    last_bright = np.zeros(shape, dtype=np.float32)
    last_bright_idx = np.full((h, w), -1, dtype=np.int32)   # per-pixel, not per-channel

    # Pass 1: forward lighten + track last bright pixel per position
    for i, path in enumerate(frame_paths):
        frame = first if i == 0 else decode_fn(path)
        bright_mask = np.any(frame > bright_threshold, axis=-1)  # (h, w)
        trail = np.maximum(trail, frame)
        last_bright = np.where(bright_mask[:, :, np.newaxis], frame, last_bright)
        last_bright_idx = np.where(bright_mask, i, last_bright_idx)

    # Pass 2: backward — find first bright pixel from the end per position
    first_bright_from_end = np.zeros(shape, dtype=np.float32)
    first_bright_from_end_idx = np.full((h, w), n, dtype=np.int32)   # per-pixel

    for i in range(n - 1, -1, -1):
        frame = first if i == 0 else decode_fn(frame_paths[i])
        bright_mask = np.any(frame > bright_threshold, axis=-1)  # (h, w)
        first_bright_from_end = np.where(bright_mask[:, :, np.newaxis], frame, first_bright_from_end)
        first_bright_from_end_idx = np.where(bright_mask, i, first_bright_from_end_idx)

    # Fill: pixels dark in trail with bright anchors on both sides
    has_left = last_bright_idx >= 0                           # (h, w)
    has_right = first_bright_from_end_idx < n                 # (h, w)
    trail_is_dark = np.all(trail <= bright_threshold, axis=-1)  # (h, w)
    gap_exists = trail_is_dark & has_left & has_right & (last_bright_idx < first_bright_from_end_idx)

    filled = np.where(gap_exists[:, :, np.newaxis],
                      (last_bright + first_bright_from_end) / 2.0,
                      trail)
    return filled
