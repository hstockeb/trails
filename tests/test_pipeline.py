import numpy as np
import pytest
from PIL import Image

from engine.models import FrameRecord, StackJob, StackOptions
from engine.pipeline import run_pipeline


def make_test_frames(tmp_path, n=5, value=0.5) -> list[FrameRecord]:
    frames = []
    for i in range(n):
        arr = np.full((50, 50, 3), int(value * 255), dtype=np.uint8)
        path = tmp_path / f"frame_{i:03d}.jpg"
        Image.fromarray(arr).save(path)
        frames.append(
            FrameRecord(
                path=str(path),
                filename=path.name,
                index=i,
                width=50,
                height=50,
                is_raw=False,
                exposure_seconds=10.0,
            )
        )
    return frames


def test_lighten_pipeline_returns_array(tmp_path):
    frames = make_test_frames(tmp_path)
    job = StackJob(frames=frames, method="lighten", options=StackOptions())
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["frames_processed"] == 5


def test_pipeline_emits_progress_events(tmp_path):
    frames = make_test_frames(tmp_path)
    job = StackJob(
        frames=frames,
        method="lighten",
        options=StackOptions(preview_every_n_frames=2),
    )
    events = list(run_pipeline(job))
    progress_events = [e for e in events if e["type"] == "progress"]
    assert len(progress_events) == 5


def test_pipeline_computes_total_exposure(tmp_path):
    frames = make_test_frames(tmp_path, n=3)
    job = StackJob(frames=frames, method="average", options=StackOptions())
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["total_exposure_seconds"] == pytest.approx(30.0)


def test_pipeline_uses_manual_exposure_when_exif_missing(tmp_path):
    frames = make_test_frames(tmp_path, n=3)
    for frame in frames:
        frame.exposure_seconds = None
    job = StackJob(
        frames=frames,
        method="lighten",
        options=StackOptions(manual_exposure_seconds=20.0),
    )
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["total_exposure_seconds"] == pytest.approx(60.0)


def test_pipeline_emits_preview_events(tmp_path):
    frames = make_test_frames(tmp_path, n=6)
    job = StackJob(frames=frames, method="lighten",
                   options=StackOptions(preview_every_n_frames=2))
    events = list(run_pipeline(job))
    previews = [e for e in events if e["type"] == "preview"]
    # Every 2 frames = 3 previews (frames 2, 4, 6)
    assert len(previews) == 3
    assert all("path" in e["payload"] for e in previews)


def test_pipeline_always_emits_final_preview(tmp_path):
    # 5 frames with interval=3: previews at frame 3 and 5 (final)
    frames = make_test_frames(tmp_path, n=5)
    job = StackJob(frames=frames, method="lighten",
                   options=StackOptions(preview_every_n_frames=3))
    events = list(run_pipeline(job))
    previews = [e for e in events if e["type"] == "preview"]
    assert len(previews) == 2


def test_pipeline_clamps_zero_preview_interval(tmp_path):
    frames = make_test_frames(tmp_path, n=3)
    job = StackJob(frames=frames, method="lighten",
                   options=StackOptions(preview_every_n_frames=0))
    # Should not raise ZeroDivisionError; clamps to 1 → preview every frame
    events = list(run_pipeline(job))
    previews = [e for e in events if e["type"] == "preview"]
    assert len(previews) == 3


def test_pipeline_hot_pixel_reduction(tmp_path):
    frames = make_test_frames(tmp_path, n=3)
    job = StackJob(frames=frames, method="lighten",
                   options=StackOptions(hot_pixel_reduction=True))
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["frames_processed"] == 3


def test_pipeline_dark_frame_subtraction(tmp_path):
    frames = make_test_frames(tmp_path, n=3, value=0.8)
    dark_arr = np.full((50, 50, 3), int(0.3 * 255), dtype=np.uint8)
    dark_path = tmp_path / "dark.jpg"
    Image.fromarray(dark_arr).save(dark_path)
    dark_record = FrameRecord(path=str(dark_path), filename="dark.jpg", index=-1,
                              width=50, height=50, is_raw=False)
    job = StackJob(frames=frames, method="lighten",
                   options=StackOptions(), dark_frame=dark_record)
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["frames_processed"] == 3


def test_pipeline_gapfill_method(tmp_path):
    frames = make_test_frames(tmp_path, n=3)
    job = StackJob(frames=frames, method="gapfill", options=StackOptions())
    events = list(run_pipeline(job))
    done = next(e for e in events if e["type"] == "done")
    assert done["payload"]["frames_processed"] == 3
