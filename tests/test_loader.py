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
