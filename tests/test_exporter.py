import numpy as np
from pathlib import Path

from engine.exporter import export_result, generate_filename
from engine.models import FrameRecord, StackJob, StackOptions, StackResult


def make_frames(n=120, exposure=30.0):
    return [
        FrameRecord(
            path=f"/tmp/IMG_{i:04d}.jpg",
            filename=f"IMG_{i:04d}.jpg",
            index=i,
            width=100,
            height=100,
            is_raw=False,
            exposure_seconds=exposure,
        )
        for i in range(1, n + 1)
    ]


def test_filename_lighten_60min():
    frames = make_frames(n=120, exposure=30.0)
    job = StackJob(frames=frames, method="lighten", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=3600.0,
        frames_processed=120,
    )
    name = generate_filename(job, result, StackOptions(output_format="jpeg"))
    assert name == "startrails_IMG_0001-IMG_0120_60min_lighten.jpg"


def test_filename_comet_73min():
    frames = make_frames(n=146, exposure=30.0)
    job = StackJob(frames=frames, method="comet", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=4380.0,
        frames_processed=146,
    )
    name = generate_filename(job, result, StackOptions(output_format="tiff"))
    assert name == "startrails_IMG_0001-IMG_0146_73min_comet.tif"


def test_filename_2h():
    frames = make_frames(n=360, exposure=20.0)
    job = StackJob(frames=frames, method="average", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=7200.0,
        frames_processed=360,
    )
    name = generate_filename(job, result, StackOptions(output_format="png"))
    assert name == "startrails_IMG_0001-IMG_0360_2h_average.png"


def test_filename_2h15min():
    frames = make_frames(n=270, exposure=30.0)
    job = StackJob(frames=frames, method="lighten", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=8100.0,
        frames_processed=270,
    )
    name = generate_filename(job, result, StackOptions(output_format="jpeg"))
    assert name == "startrails_IMG_0001-IMG_0270_2h15min_lighten.jpg"


def test_filename_unknown_exposure():
    frames = make_frames(n=10, exposure=0)
    for frame in frames:
        frame.exposure_seconds = None
    job = StackJob(frames=frames, method="lighten", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=None,
        frames_processed=10,
    )
    name = generate_filename(job, result, StackOptions(output_format="jpeg"))
    assert name == "startrails_IMG_0001-IMG_0010_unknown-exposure_lighten.jpg"


def test_filename_sanitises_unsafe_chars(tmp_path):
    frames = [
        FrameRecord(
            path=str(tmp_path / "A:B.jpg"),
            filename="A:B.jpg",
            index=0,
            width=10,
            height=10,
            is_raw=False,
        ),
        FrameRecord(
            path=str(tmp_path / "C*D.jpg"),
            filename="C*D.jpg",
            index=1,
            width=10,
            height=10,
            is_raw=False,
        ),
    ]
    job = StackJob(frames=frames, method="lighten", options=StackOptions())
    result = StackResult(
        output_path="",
        filename="",
        total_exposure_seconds=None,
        frames_processed=2,
    )
    name = generate_filename(job, result, StackOptions(output_format="jpeg"))
    assert ":" not in name
    assert "*" not in name


def test_export_writes_jpeg(tmp_path):
    arr = np.full((50, 50, 3), 0.5, dtype=np.float32)
    out = str(tmp_path / "out.jpg")
    export_result(arr, out, output_format="jpeg", jpeg_quality=85)
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0


def test_export_applies_resize(tmp_path):
    arr = np.full((100, 100, 3), 0.5, dtype=np.float32)
    out = str(tmp_path / "out.png")
    export_result(arr, out, output_format="png", resize=(50, 50))
    from PIL import Image

    with Image.open(out) as img:
        assert img.size == (50, 50)
