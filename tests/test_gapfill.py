import numpy as np
import pytest
from engine.methods.gapfill import stack as gapfill_stack

def make_frame_array(value: float, shape=(4, 4, 3)) -> np.ndarray:
    return np.full(shape, value, dtype=np.float32)

def decode_fn(path):
    """Fake decoder: path encodes brightness as float string."""
    return make_frame_array(float(path))

def test_gapfill_fills_dark_gap_between_bright_frames():
    # bright→dark→bright: gap should be filled with average of anchors
    paths = ["0.8", "0.0", "0.9"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, (0.8 + 0.9) / 2.0)

def test_gapfill_differs_from_maximum():
    # A plain np.maximum would give 0.9; gap fill gives the average 0.85
    paths = ["0.8", "0.0", "0.9"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert not np.allclose(result, 0.9), "gap fill must differ from plain lighten/max"

def test_gapfill_no_gap_unchanged():
    # All bright — no gap detected, result is plain lighten
    paths = ["0.8", "0.9", "0.7"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, 0.9)

def test_gapfill_gap_at_start_not_filled():
    # Dark frame first — no left anchor, so no gap fill
    paths = ["0.0", "0.8"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, 0.8)

def test_gapfill_trailing_gap_not_filled():
    # bright→dark at end with no right anchor: no gap fill, falls back to lighten
    paths = ["0.8", "0.0"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, 0.8)

def test_gapfill_single_frame():
    paths = ["0.5"]
    result = gapfill_stack(paths, decode_fn, bright_threshold=0.1)
    assert np.allclose(result, 0.5)

def test_gapfill_raises_on_empty_paths():
    with pytest.raises(ValueError):
        gapfill_stack([], decode_fn)
