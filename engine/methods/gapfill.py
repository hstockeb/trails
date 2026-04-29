import numpy as np
from typing import Callable

def stack(frame_paths: list[str],
          decode_fn: Callable[[str], np.ndarray],
          bright_threshold: float = 0.05) -> np.ndarray:
    """
    Two-pass gap fill. Detects bright→dark→bright sequences per pixel and fills
    the dark region with the average of the bounding bright values. Pixels without
    a confirmed gap fall back to a plain lighten (max) result.
    """
    if not frame_paths:
        raise ValueError("frame_paths is empty")

    n = len(frame_paths)
    first = decode_fn(frame_paths[0])
    h, w, c = first.shape

    trail = np.zeros((h, w, c), dtype=np.float32)
    last_bright_val = np.zeros((h, w, c), dtype=np.float32)
    last_bright_idx = np.full((h, w), -1, dtype=np.int32)

    # Left anchor: value captured when a pixel first transitions bright → dark
    gap_left_val = np.zeros((h, w, c), dtype=np.float32)
    in_gap = np.zeros((h, w), dtype=bool)
    has_gap = np.zeros((h, w), dtype=bool)  # confirmed bright→dark→bright

    # Pass 1 (forward): detect gap entry/exit and build lighten trail
    for i, path in enumerate(frame_paths):
        frame = first if i == 0 else decode_fn(path)
        bright = np.any(frame > bright_threshold, axis=-1)
        dark = ~bright

        trail = np.maximum(trail, frame)

        # Entering a gap: pixel transitions from bright to dark
        entering_gap = dark & (last_bright_idx >= 0) & ~in_gap
        gap_left_val = np.where(entering_gap[:, :, np.newaxis], last_bright_val, gap_left_val)
        in_gap = in_gap | entering_gap

        # Exiting a gap: pixel turns bright again — gap is confirmed
        exiting_gap = bright & in_gap
        has_gap = has_gap | exiting_gap
        in_gap = in_gap & ~exiting_gap

        last_bright_val = np.where(bright[:, :, np.newaxis], frame, last_bright_val)
        last_bright_idx = np.where(bright, i, last_bright_idx)

    # Pass 2 (backward): find right anchor = rightmost bright frame (first found scanning right→left)
    right_anchor_val = np.zeros((h, w, c), dtype=np.float32)
    right_anchor_found = np.zeros((h, w), dtype=bool)

    for i in range(n - 1, -1, -1):
        frame = first if i == 0 else decode_fn(frame_paths[i])
        bright = np.any(frame > bright_threshold, axis=-1)
        new_find = bright & ~right_anchor_found
        right_anchor_val = np.where(new_find[:, :, np.newaxis], frame, right_anchor_val)
        right_anchor_found = right_anchor_found | new_find

    # Fill confirmed gap pixels; all others keep the lighten result
    return np.where(
        has_gap[:, :, np.newaxis],
        (gap_left_val + right_anchor_val) / 2.0,
        trail,
    )
