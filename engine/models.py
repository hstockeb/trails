from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class FrameRecord:
    path: str
    filename: str
    index: int
    width: int
    height: int
    is_raw: bool
    capture_time: datetime | None = None
    exposure_seconds: float | None = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "filename": self.filename,
            "index": self.index,
            "width": self.width,
            "height": self.height,
            "is_raw": self.is_raw,
            "capture_time": self.capture_time.isoformat() if self.capture_time else None,
            "exposure_seconds": self.exposure_seconds,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FrameRecord":
        ct = datetime.fromisoformat(d["capture_time"]) if d.get("capture_time") else None
        return cls(
            path=d["path"], filename=d["filename"], index=d["index"],
            width=d["width"], height=d["height"], is_raw=d["is_raw"],
            capture_time=ct, exposure_seconds=d.get("exposure_seconds"),
        )


@dataclass
class StackOptions:
    hot_pixel_reduction: bool = False
    align_frames: bool = False
    output_format: Literal["jpeg", "png", "tiff"] = "jpeg"
    jpeg_quality: int = 85
    resize: tuple[int, int] | None = None
    crop: tuple[int, int, int, int] | None = None   # x, y, w, h
    gpu: bool = False
    preview_every_n_frames: int = 10
    manual_exposure_seconds: float | None = None

    def to_dict(self) -> dict:
        return {
            "hot_pixel_reduction": self.hot_pixel_reduction,
            "align_frames": self.align_frames,
            "output_format": self.output_format,
            "jpeg_quality": self.jpeg_quality,
            "resize": list(self.resize) if self.resize else None,
            "crop": list(self.crop) if self.crop else None,
            "gpu": self.gpu,
            "preview_every_n_frames": self.preview_every_n_frames,
            "manual_exposure_seconds": self.manual_exposure_seconds,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StackOptions":
        return cls(
            hot_pixel_reduction=d.get("hot_pixel_reduction", False),
            align_frames=d.get("align_frames", False),
            output_format=d.get("output_format", "jpeg"),
            jpeg_quality=d.get("jpeg_quality", 85),
            resize=tuple(d["resize"]) if d.get("resize") else None,
            crop=tuple(d["crop"]) if d.get("crop") else None,
            gpu=d.get("gpu", False),
            preview_every_n_frames=d.get("preview_every_n_frames", 10),
            manual_exposure_seconds=d.get("manual_exposure_seconds"),
        )


@dataclass
class StackJob:
    frames: list[FrameRecord]
    method: Literal["lighten", "maximum", "average", "gapfill", "comet"]
    options: StackOptions
    dark_frame: FrameRecord | None = None

    def to_dict(self) -> dict:
        return {
            "frames": [f.to_dict() for f in self.frames],
            "method": self.method,
            "options": self.options.to_dict(),
            "dark_frame": self.dark_frame.to_dict() if self.dark_frame else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StackJob":
        return cls(
            frames=[FrameRecord.from_dict(f) for f in d["frames"]],
            method=d["method"],
            options=StackOptions.from_dict(d.get("options", {})),
            dark_frame=FrameRecord.from_dict(d["dark_frame"]) if d.get("dark_frame") else None,
        )


@dataclass
class StackResult:
    output_path: str
    filename: str
    total_exposure_seconds: float | None
    frames_processed: int

    def to_dict(self) -> dict:
        return {
            "output_path": self.output_path,
            "filename": self.filename,
            "total_exposure_seconds": self.total_exposure_seconds,
            "frames_processed": self.frames_processed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StackResult":
        return cls(
            output_path=d["output_path"],
            filename=d["filename"],
            total_exposure_seconds=d.get("total_exposure_seconds"),
            frames_processed=d["frames_processed"],
        )
