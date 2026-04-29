from datetime import datetime
from unittest.mock import patch, MagicMock
from engine.loader import scan_folder, sort_frames
from engine.models import FrameRecord

def test_scan_folder_finds_images(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    assert len(frames) == 5
    assert all(isinstance(f, FrameRecord) for f in frames)

def test_scan_folder_sets_width_height(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    assert frames[0].width == 100
    assert frames[0].height == 100

def test_scan_folder_sets_index(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    assert [f.index for f in frames] == [0, 1, 2, 3, 4]

def test_sort_by_filename(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    sorted_frames = sort_frames(frames, by="filename")
    names = [f.filename for f in sorted_frames]
    assert names == sorted(names)

def test_scan_ignores_non_images(tmp_image_folder):
    (tmp_image_folder / "readme.txt").write_text("ignore me")
    frames = scan_folder(str(tmp_image_folder))
    assert len(frames) == 5

def test_scan_ignores_directories_with_image_extension(tmp_image_folder):
    fake_dir = tmp_image_folder / "subdir.jpg"
    fake_dir.mkdir()
    frames = scan_folder(str(tmp_image_folder))
    assert len(frames) == 5

def test_scan_reads_exif_capture_time(tmp_image_folder):
    fake_time = datetime(2024, 8, 15, 22, 30, 0)
    fake_exposure_tag = MagicMock()
    fake_exposure_tag.values = [MagicMock(num=30, den=1)]
    tags = {
        "EXIF DateTimeOriginal": MagicMock(__str__=lambda s: "2024:08:15 22:30:00"),
        "EXIF ExposureTime": fake_exposure_tag,
    }
    with patch("exifread.process_file", return_value=tags):
        frames = scan_folder(str(tmp_image_folder))
    assert frames[0].capture_time == fake_time
    assert frames[0].exposure_seconds == 30.0

def test_scan_handles_missing_exif_gracefully(tmp_image_folder):
    with patch("exifread.process_file", return_value={}):
        frames = scan_folder(str(tmp_image_folder))
    assert all(f.capture_time is None for f in frames)
    assert all(f.exposure_seconds is None for f in frames)

def test_sort_by_timestamp(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    times = [datetime(2024, 1, 1, 0, i, 0) for i in range(5)]
    for f, t in zip(frames, reversed(times)):
        f.capture_time = t
    sorted_frames = sort_frames(frames, by="timestamp")
    result_times = [f.capture_time for f in sorted_frames]
    assert result_times == sorted(result_times)

def test_sort_by_timestamp_puts_no_exif_last(tmp_image_folder):
    frames = scan_folder(str(tmp_image_folder))
    frames[0].capture_time = datetime(2024, 1, 1, 0, 0, 0)
    # rest have no capture_time
    sorted_frames = sort_frames(frames, by="timestamp")
    assert sorted_frames[0].capture_time is not None
    assert all(f.capture_time is None for f in sorted_frames[1:])
