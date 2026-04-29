import os
from pathlib import Path
from datetime import datetime
from engine.models import FrameRecord

RAW_EXTENSIONS = {'.cr2', '.cr3', '.arw', '.nef', '.dng', '.orf', '.rw2'}
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'} | RAW_EXTENSIONS


def scan_folder(folder: str) -> list[FrameRecord]:
    paths = sorted(
        p for p in Path(folder).iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    records = []
    for i, path in enumerate(paths):
        capture_time, exposure, w, h = _read_exif(str(path))
        records.append(FrameRecord(
            path=str(path),
            filename=path.name,
            index=i,
            width=w,
            height=h,
            is_raw=path.suffix.lower() in RAW_EXTENSIONS,
            capture_time=capture_time,
            exposure_seconds=exposure,
        ))
    return records


def sort_frames(frames: list[FrameRecord], by: str = "filename") -> list[FrameRecord]:
    if by == "timestamp":
        frames_with_time = [f for f in frames if f.capture_time is not None]
        frames_without = [f for f in frames if f.capture_time is None]
        sorted_frames = sorted(frames_with_time, key=lambda f: f.capture_time)
        sorted_frames += sorted(frames_without, key=lambda f: f.filename)
    else:
        sorted_frames = sorted(frames, key=lambda f: f.filename)
    for i, f in enumerate(sorted_frames):
        f.index = i
    return sorted_frames


def _read_exif(path: str) -> tuple[datetime | None, float | None, int, int]:
    ext = Path(path).suffix.lower()
    capture_time = None
    exposure = None

    try:
        import exifread
        with open(path, 'rb') as fh:
            tags = exifread.process_file(fh, details=False)
        if 'EXIF DateTimeOriginal' in tags:
            try:
                capture_time = datetime.strptime(
                    str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass
        if 'EXIF ExposureTime' in tags:
            val = tags['EXIF ExposureTime'].values[0]
            exposure = float(val.num) / float(val.den) if val.den != 0 else None
    except Exception:
        pass

    if ext in RAW_EXTENSIONS:
        try:
            import rawpy
            with rawpy.imread(path) as raw:
                h, w = raw.raw_image_visible.shape[:2]
        except Exception:
            w, h = 0, 0
    else:
        try:
            from PIL import Image
            with Image.open(path) as img:
                w, h = img.size
        except Exception:
            w, h = 0, 0

    return capture_time, exposure, w, h
