import numpy as np
import pytest
from engine.methods.gapfill import stack as gapfill_stack

def make_frame_array(value: float, shape=(4, 4, 3)) -> np.ndarray:
    return np.full(shape, value, dtype=np.float32)

def decode_fn(path):
    """Fake decoder: path encodes brightness as float string."""
    return make_frame_array(float(path))

def test_gapfill_fills_dark_gap_between_bright_frames():
    # Frame sequence: bright, dark, bright
    paths = ["0.8", "0.0", "0.9"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    # All pixels should be filled (non-zero)
    assert np.all(result > 0)

def test_gapfill_no_gap_unchanged():
    paths = ["0.8", "0.9", "0.7"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, 0.9)

def test_gapfill_gap_at_start_not_filled():
    # Dark, bright — no left anchor to interpolate from
    paths = ["0.0", "0.8"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    # Only second frame contributes; first stays 0
    assert np.allclose(result, 0.8)
