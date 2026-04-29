# Stacker — Design Spec

**Date:** 2026-04-29  
**Status:** Approved

---

## Overview

Stacker is a macOS desktop application for stacking multiple night-sky images to create star trails. It uses a SwiftUI native shell for the UI and a bundled Python subprocess for all image processing, communicating over a local Unix domain socket.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| UI shell | Swift / SwiftUI (macOS native) |
| Image engine | Python 3.11+, NumPy, Pillow, rawpy (LibRaw) |
| IPC | Unix domain socket, length-prefixed JSON messages |
| RAW decoding | rawpy (LibRaw bindings) |
| GPU (future) | Metal / OpenCL via a swappable backend interface |

---

## Architecture

```
Stacker.app
├── SwiftUI Frontend
│   ├── Views: FolderPicker, FrameList, SettingsPanel, PreviewPane, ProgressBar
│   └── EngineClient   ← manages Python subprocess lifecycle + IPC
│
└── Python Engine (subprocess, bundled inside .app)
    ├── main.py          ← Unix socket server, dispatches jobs
    ├── loader.py        ← file discovery, EXIF reading, sorting
    ├── pipeline.py      ← streaming frame pipeline
    ├── backends/
    │   ├── cpu.py       ← NumPy operations (current)
    │   └── gpu.py       ← Metal/OpenCL (future)
    ├── methods/         ← one file per stacking method (strategy pattern)
    │   ├── lighten.py
    │   ├── maximum.py
    │   ├── average.py
    │   ├── gapfill.py
    │   └── comet.py
    └── exporter.py      ← output encoding and filename generation
```

### IPC Protocol

Swift launches the Python engine on app start and communicates over a Unix domain socket using length-prefixed JSON messages.

**Swift → Python (commands):**
```json
{ "type": "scan_folder",  "payload": { "path": "/path/to/folder" } }
{ "type": "start_stack",  "payload": <StackJob> }
{ "type": "cancel" }
{ "type": "export",       "payload": { "output_path": "/path/to/out.jpg", "format": "jpeg", "quality": 85, "resize": null, "crop": null } }
```

`start_stack` runs the stacking pipeline and writes the result to a temporary file (`/tmp/stacker_result_<uuid>`). It emits `done` with the temp path. `export` re-encodes that temp result to the user's final destination with the chosen format and quality. This separation allows the user to adjust output settings (format, quality, resize, crop) without re-stacking.

**Python → Swift (events):**
```json
{ "type": "scan_complete", "payload": [<FrameRecord>, ...] }
{ "type": "progress",      "payload": { "frame": 42, "total": 120 } }
{ "type": "preview",       "payload": { "path": "/tmp/preview.jpg" } }
{ "type": "done",          "payload": <StackResult> }
{ "type": "error",         "payload": { "message": "..." } }
```

---

## Feature List

### Input
- Folder picker and drag-and-drop folder support
- Supported formats: JPEG, PNG, TIFF, RAW (CR2, CR3, ARW, NEF, DNG, ORF, RW2)
- Sort by filename or EXIF capture timestamp
- Frame range selector (first frame / last frame by filename)
- Frame count display
- Total exposure display (from EXIF, or manual entry fallback)

### Stacking Methods
- **Lighten blend** — pixel-wise maximum per channel (standard star trails)
- **Maximum blend** — same math as lighten; reserved for per-channel-only future variant
- **Average blend** — running mean; useful for noise reduction
- **Gap fill** — two-pass; fills dark gaps between trail segments caused by pause between exposures
- **Comet mode** — exponential decay accumulation; recent frames bright, older frames fade

### Options
- Output format: JPEG / PNG / TIFF
- JPEG quality (0–100, default 85)
- Resize output (width × height, aspect-ratio locked)
- Crop (rectangle drawn on preview)
- Dark-frame subtraction (single dark frame, optional)
- Hot-pixel reduction (median filter on isolated bright pixels, optional)
- Alignment toggle (default off — fixed-tripod star trails do not need alignment)
- Processing backend: CPU (active) / GPU (toggle grayed out until implemented)
- Preview refresh rate (every N frames, configurable)

### Processing UX
- Live preview panel, refreshes every N frames
- Progress bar with frame counter and ETA
- Cancel button (graceful abort, preserves partial result for inspection)
- Auto-generated output filename
- "Reveal in Finder" on export completion

---

## User Workflow

```
1. Launch app
   └── Python engine starts silently in background

2. Select source folder (picker or drag-and-drop)
   └── Python scans folder → returns sorted FrameRecord list
   └── SwiftUI displays frame list

3. Configure
   ├── Set frame range (first / last filename)
   ├── Choose sort order (filename or EXIF timestamp)
   ├── Enter manual exposure per frame if EXIF missing
   ├── Select stacking method
   └── Set output options (format, quality, resize, crop, dark frame, hot pixels)

4. Preview (optional)
   └── Run stack on downscaled frames → display in PreviewPane

5. Stack
   ├── Progress bar updates per frame
   ├── Preview pane refreshes every N frames
   └── Cancel available at any time

6. Export
   ├── Output written to source folder (or user-chosen output folder)
   ├── Filename auto-generated from range + exposure + method
   └── "Reveal in Finder" shown on completion
```

---

## Data Model

```python
FrameRecord:
  path: str
  filename: str                   # basename only, e.g. "IMG_0042.CR3"
  index: int                      # position in sorted list
  capture_time: datetime | None   # from EXIF DateTimeOriginal
  exposure_seconds: float | None  # from EXIF ExposureTime
  width: int
  height: int
  is_raw: bool

StackJob:
  frames: list[FrameRecord]       # sorted and range-filtered
  method: Literal["lighten", "maximum", "average", "gapfill", "comet"]
  dark_frame: FrameRecord | None
  options: StackOptions

StackOptions:
  hot_pixel_reduction: bool       # default False
  align_frames: bool              # default False
  output_format: Literal["jpeg", "png", "tiff"]
  jpeg_quality: int               # default 85
  resize: tuple[int, int] | None  # None = no resize
  crop: tuple[int, int, int, int] | None  # (x, y, w, h); None = no crop
  gpu: bool                       # default False
  preview_every_n_frames: int     # default 10

StackResult:
  output_path: str
  filename: str
  total_exposure_seconds: float | None
  frames_processed: int
```

---

## Processing Pipeline

```
pipeline.run(job)

  initialize accumulator from first frame (float32, shape [H, W, 3])

  for each frame in job.frames (streaming — one frame in memory at a time):
    1. decode_frame(path)             → numpy float32 [H, W, 3]
       - rawpy.imread()  if is_raw
       - Pillow + np     otherwise
    2. subtract_dark(frame, dark)     → if dark_frame is set
    3. reduce_hot_pixels(frame)       → if hot_pixel_reduction is True
    4. align(frame, reference)        → if align_frames is True
    5. backend.blend(accumulator, frame, method, frame_index, total_frames)
    6. emit progress event { frame: i, total: N }
    7. if i % preview_every_n_frames == 0: write /tmp/preview.jpg, emit preview event

  post_process(accumulator, options):
    → crop → resize → clip to [0, 255] → convert to uint8

  export(accumulator, options):
    → encode to output_format
    → write to output_path
    → emit done event
```

**Gap fill note:** `gapfill` requires two passes. Pass 1 is a lighten blend that records a per-pixel metadata structure (last bright frame index, gap counter). Pass 2 fills dark gaps by interpolating between flanking bright pixels. The pipeline switches to a two-pass mode automatically when `method == "gapfill"`.

---

## Stacking Methods — Pseudocode

### Lighten blend
```python
def blend(accumulator, frame, **_):
    return np.maximum(accumulator, frame)
```

### Maximum blend
```python
def blend(accumulator, frame, **_):
    return np.maximum(accumulator, frame)
# Same math as lighten. Reserved for a future luminance-only lighten variant.
```

### Average blend (online / streaming Welford mean)
```python
def blend(accumulator, frame, frame_index, **_):
    n = frame_index + 1
    return accumulator + (frame - accumulator) / n
```

### Gap fill (two-pass)
```python
# Pass 1: lighten blend, record gap metadata per pixel
for i, frame in enumerate(frames):
    for each pixel (x, y):
        if frame[x,y] > BRIGHT_THRESHOLD:
            trail_map[x,y] = max(trail_map[x,y], frame[x,y])
            gap_meta[x,y].last_bright_index = i
            gap_meta[x,y].gap_count = 0
        else:
            gap_meta[x,y].gap_count += 1

# Pass 2: fill gaps
for each pixel (x, y):
    if trail_map[x,y] is dark AND gap_meta[x,y] has flanking bright segments:
        trail_map[x,y] = interpolate(left_bright_value, right_bright_value)
```

### Comet mode (exponential decay)
```python
DECAY = 0.97  # configurable; lower = shorter, brighter comet head

def blend(accumulator, frame, **_):
    return np.maximum(accumulator * DECAY, frame)
# Each prior frame's contribution decays by DECAY per subsequent frame.
# Result: bright head at the most recent position, fading tail trailing behind.
```

---

## Filename Generation

```python
import re

def generate_filename(job: StackJob, result: StackResult, options: StackOptions) -> str:
    first = sanitize(Path(job.frames[0].filename).stem)
    last  = sanitize(Path(job.frames[-1].filename).stem)
    range_str = f"{first}-{last}"

    if result.total_exposure_seconds is None:
        exposure_str = "unknown-exposure"
    else:
        mins = result.total_exposure_seconds / 60
        if mins < 60:
            exposure_str = f"{round(mins)}min"
        else:
            h = int(mins // 60)
            m = int(mins % 60)
            exposure_str = f"{h}h{m}min" if m > 0 else f"{h}h"

    method_str = job.method  # lighten | maximum | average | gapfill | comet
    ext = options.output_format  # jpeg | png | tiff

    raw = f"startrails_{range_str}_{exposure_str}_{method_str}.{ext}"
    return sanitize(raw)

def sanitize(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]', '_', s)
```

**Examples:**
```
startrails_IMG_0001-IMG_0120_60min_lighten.jpg
startrails_DSC01234-DSC01380_73min_comet.tif
startrails_A7RIII_0001-A7RIII_0240_2h_gapfill.png
startrails_IMG_0001-IMG_0050_unknown-exposure_average.png
```

---

## Future Improvements

- **GPU backend** — Metal compute shaders implement the same `blend()` interface; activated via the GPU toggle in settings
- **Batch processing** — queue multiple folder/method combinations for overnight runs
- **Timelapse export** — output intermediate frames as a numbered sequence for ffmpeg video encoding
- **Interval gap detection** — automatically detect missing frames (by timestamp gaps) and warn before stacking
- **Histogram display** — live per-channel histogram during stacking
- **Mask painting** — exclude regions (foreground objects) from stacking
- **Foreground blending** — composite a best-exposed foreground frame with the trail result
- **Windows / Linux port** — the Python engine is fully cross-platform; a future Qt shell could reuse it unchanged; only the SwiftUI shell is macOS-specific
