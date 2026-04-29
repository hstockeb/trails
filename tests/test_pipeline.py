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
