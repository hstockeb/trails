import os
import tempfile
from pathlib import Path
from typing import Generator

import numpy as np

from engine.backends.cpu import CPUBackend
from engine.methods.gapfill import stack as gapfill_stack
from engine.models import StackJob

RAW_EXTENSIONS = {".cr2", ".cr3", ".arw", ".nef", ".dng", ".orf", ".rw2"}


def decode_frame(path: str) -> np.ndarray:
    ext = Path(path).suffix.lower()
    if ext in RAW_EXTENSIONS:
        import rawpy

        with rawpy.imread(path) as raw:
            rgb = raw.postprocess()
        return rgb.astype(np.float32) / 255.0

    from PIL import Image

    with Image.open(path) as img:
        return np.array(img.convert("RGB"), dtype=np.float32) / 255.0


def _compute_total_exposure(job: StackJob) -> float | None:
    if all(frame.exposure_seconds is not None for frame in job.frames):
        return sum(frame.exposure_seconds for frame in job.frames)
    if job.options.manual_exposure_seconds is not None:
        return job.options.manual_exposure_seconds * len(job.frames)
    return None


def run_pipeline(job: StackJob) -> Generator[dict, None, None]:
    if job.method == "gapfill":
        yield from _run_gapfill(job)
        return

    backend = CPUBackend()
    frame_count = len(job.frames)
    accumulator = None

    dark = decode_frame(job.dark_frame.path) if job.dark_frame else None

    for index, frame_record in enumerate(job.frames):
        frame = decode_frame(frame_record.path)

        if dark is not None:
            frame = np.clip(frame - dark, 0.0, 1.0)

        if accumulator is None:
            accumulator = frame.copy()
        else:
            accumulator = backend.blend(
                accumulator,
                frame,
                job.method,
                index,
                frame_count,
            )

        yield {"type": "progress", "payload": {"frame": index + 1, "total": frame_count}}

        if (index + 1) % job.options.preview_every_n_frames == 0 or index == frame_count - 1:
            preview_path = _write_preview(accumulator)
            yield {"type": "preview", "payload": {"path": preview_path}}

    tmp_result = _write_preview(accumulator, suffix=".npy", as_npy=True)
    yield {
        "type": "done",
        "payload": {
            "tmp_result_path": tmp_result,
            "total_exposure_seconds": _compute_total_exposure(job),
            "frames_processed": frame_count,
        },
    }


def _run_gapfill(job: StackJob) -> Generator[dict, None, None]:
    paths = [frame.path for frame in job.frames]
    frame_count = len(paths)
    yield {"type": "progress", "payload": {"frame": 0, "total": frame_count, "pass": 1}}

    result = gapfill_stack(paths, decode_frame)

    preview_path = _write_preview(result)
    yield {"type": "preview", "payload": {"path": preview_path}}

    tmp_result = _write_preview(result, suffix=".npy", as_npy=True)
    yield {
        "type": "done",
        "payload": {
            "tmp_result_path": tmp_result,
            "total_exposure_seconds": _compute_total_exposure(job),
            "frames_processed": frame_count,
        },
    }


def _write_preview(arr: np.ndarray, suffix=".jpg", as_npy=False) -> str:
    fd, path = tempfile.mkstemp(prefix="stacker_", suffix=suffix)
    os.close(fd)
    if as_npy:
        np.save(path, arr)
        return path

    from PIL import Image

    image = Image.fromarray((np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8))
    image.save(path, quality=80)
    return path
