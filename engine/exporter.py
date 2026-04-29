import re
from pathlib import Path

import numpy as np

from engine.models import StackJob, StackOptions, StackResult

_UNSAFE = re.compile(r'[\\/:*?"<>|\s]')
EXT_MAP = {"jpeg": "jpg", "png": "png", "tiff": "tif"}


def sanitize(value: str) -> str:
    return _UNSAFE.sub("_", value)


def generate_filename(job: StackJob, result: StackResult, options: StackOptions) -> str:
    first_stem = Path(job.frames[0].filename).stem
    last_stem = Path(job.frames[-1].filename).stem
    range_str = f"{sanitize(first_stem)}-{sanitize(last_stem)}"

    if result.total_exposure_seconds is None:
        exposure_str = "unknown-exposure"
    else:
        minutes = round(result.total_exposure_seconds / 60.0)
        if minutes < 120:
            exposure_str = f"{minutes}min"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            exposure_str = (
                f"{hours}h{remaining_minutes}min"
                if remaining_minutes > 0
                else f"{hours}h"
            )

    ext = EXT_MAP.get(options.output_format, options.output_format)
    return sanitize(f"startrails_{range_str}_{exposure_str}_{job.method}.{ext}")


def export_result(
    arr: np.ndarray,
    output_path: str,
    output_format: str = "jpeg",
    jpeg_quality: int = 85,
    resize: tuple[int, int] | None = None,
    crop: tuple[int, int, int, int] | None = None,
) -> None:
    from PIL import Image

    image_array = (np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)
    image = Image.fromarray(image_array)

    if crop:
        x, y, width, height = crop
        image = image.crop((x, y, x + width, y + height))

    if resize:
        image = image.resize(resize, Image.LANCZOS)

    if output_format == "jpeg":
        image.save(
            output_path,
            format="JPEG",
            quality=jpeg_quality,
            subsampling=0,
            optimize=True,
        )
        return
    if output_format == "png":
        image.save(output_path, format="PNG", optimize=True)
        return
    if output_format in {"tiff", "tif"}:
        image.save(output_path, format="TIFF")
        return
    raise ValueError(f"Unknown output format: {output_format}")
