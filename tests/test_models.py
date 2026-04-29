from engine.models import FrameRecord, StackJob, StackOptions, StackResult
from datetime import datetime

def test_frame_record_defaults():
    f = FrameRecord(path="/tmp/IMG_0001.jpg", filename="IMG_0001.jpg", index=0,
                    width=100, height=100, is_raw=False)
    assert f.capture_time is None
    assert f.exposure_seconds is None

def test_stack_options_defaults():
    opts = StackOptions()
    assert opts.output_format == "jpeg"
    assert opts.jpeg_quality == 85
    assert opts.align_frames is False
    assert opts.hot_pixel_reduction is False
    assert opts.gpu is False
    assert opts.preview_every_n_frames == 10
    assert opts.manual_exposure_seconds is None

def test_stack_result_serialisation():
    r = StackResult(output_path="/tmp/out.jpg", filename="out.jpg",
                    total_exposure_seconds=3600.0, frames_processed=120)
    d = r.to_dict()
    assert d["frames_processed"] == 120
    assert d["total_exposure_seconds"] == 3600.0

def test_stack_job_roundtrip():
    frames = [FrameRecord(path="/tmp/IMG_0001.jpg", filename="IMG_0001.jpg",
                          index=0, width=100, height=100, is_raw=False,
                          exposure_seconds=30.0)]
    opts = StackOptions(jpeg_quality=90)
    job = StackJob(frames=frames, method="lighten", options=opts)
    d = job.to_dict()
    restored = StackJob.from_dict(d)
    assert restored.method == "lighten"
    assert restored.frames[0].filename == "IMG_0001.jpg"
    assert restored.options.jpeg_quality == 90

def test_stack_result_roundtrip():
    r = StackResult(output_path="/tmp/out.jpg", filename="out.jpg",
                    total_exposure_seconds=3600.0, frames_processed=120)
    d = r.to_dict()
    restored = StackResult.from_dict(d)
    assert restored.frames_processed == 120
    assert restored.total_exposure_seconds == 3600.0
    assert restored.output_path == "/tmp/out.jpg"
