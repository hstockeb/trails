import numpy as np
import pytest

def make_frame(value: float, shape=(4, 4, 3)) -> np.ndarray:
    return np.full(shape, value, dtype=np.float32)

# --- Lighten ---
from engine.methods.lighten import blend as lighten_blend

def test_lighten_takes_maximum():
    acc = make_frame(0.3)
    frame = make_frame(0.7)
    result = lighten_blend(acc, frame, frame_index=1, total_frames=10)
    assert np.allclose(result, 0.7)

def test_lighten_keeps_accumulator_when_frame_is_darker():
    acc = make_frame(0.8)
    frame = make_frame(0.2)
    result = lighten_blend(acc, frame, frame_index=1, total_frames=10)
    assert np.allclose(result, 0.8)

# --- Maximum (same math as lighten) ---
from engine.methods.maximum import blend as maximum_blend

def test_maximum_same_as_lighten():
    acc = make_frame(0.5)
    frame = make_frame(0.9)
    assert np.allclose(
        lighten_blend(acc, frame, 1, 10),
        maximum_blend(acc, frame, 1, 10)
    )

# --- Average ---
from engine.methods.average import blend as average_blend

def test_average_first_frame():
    acc = make_frame(0.0)
    frame = make_frame(0.6)
    result = average_blend(acc, frame, frame_index=0, total_frames=10)
    assert np.allclose(result, 0.6)

def test_average_running_mean():
    acc = make_frame(0.4)    # mean of first 2 frames was 0.4
    frame = make_frame(1.0)  # third frame
    result = average_blend(acc, frame, frame_index=2, total_frames=10)
    # new mean = 0.4 + (1.0 - 0.4) / 3 = 0.4 + 0.2 = 0.6
    assert np.allclose(result, 0.6)

# --- Comet ---
from engine.methods.comet import blend as comet_blend

def test_comet_applies_decay_to_accumulator():
    acc = make_frame(1.0)
    frame = make_frame(0.0)  # dark frame — trail should decay
    result = comet_blend(acc, frame, frame_index=1, total_frames=10, decay=0.9)
    assert np.allclose(result, 0.9)

def test_comet_new_bright_pixel_wins_over_decayed():
    acc = make_frame(0.1)
    frame = make_frame(0.8)
    result = comet_blend(acc, frame, frame_index=1, total_frames=10, decay=0.9)
    assert np.allclose(result, 0.8)
