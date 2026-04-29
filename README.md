# Trails

A native macOS desktop app for stacking multiple night-sky images into star trails.

---

## Overview

Trails uses a **SwiftUI shell** for the native macOS UI and a **Python subprocess** for all image processing. They communicate via newline-delimited JSON over stdin/stdout pipes, keeping the architecture simple and the Python engine fully testable without the app.

## Features

- **Folder picker** with drag-and-drop support
- **Supported formats:** JPEG, PNG, TIFF, RAW (CR2, CR3, ARW, NEF, DNG, ORF, RW2)
- **5 stacking methods:**
  - **Lighten / Maximum** — pixel-wise maximum per channel (standard star trails)
  - **Average** — streaming Welford mean (noise reduction)
  - **Gap fill** — two-pass interpolation to bridge dark gaps between trail segments
  - **Comet mode** — exponential decay accumulation (bright head, fading tail)
- **Live preview** that refreshes every N frames during stacking
- **Dark frame subtraction** (optional)
- **Hot-pixel reduction** (optional)
- **Auto-generated output filenames** — e.g. `startrails_IMG_0001-IMG_0120_60min_lighten.jpg`
- **Export** to JPEG, PNG, or TIFF with resize and crop options
- **Cancel** at any time, with partial result preserved

---

## Architecture

```
Trails.app
├── SwiftUI Shell (macOS)
│   ├── EngineClient.swift    — launches Python subprocess, reads stdout
│   ├── AppState.swift        — @Observable source of truth
│   └── Views/               — FolderPicker, FrameList, Settings, Preview, Progress
│
└── Python Engine (subprocess)
    ├── server.py             — stdin/stdout dispatcher
    ├── loader.py             — folder scan, EXIF reading
    ├── pipeline.py           — streaming frame pipeline
    ├── methods/              — lighten, maximum, average, comet, gapfill
    ├── backends/cpu.py       — NumPy backend
    └── exporter.py           — post-process, encode, filename generation
```

**IPC:** Each command/event is one JSON line on stdin (Swift→Python) or stdout (Python→Swift).

```
Swift → Python:   {"type": "scan_folder", "payload": {"path": "/path/to/folder"}}
Python → Swift:   {"type": "scan_complete", "payload": [...frames...]}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI shell | Swift 5.9+ / SwiftUI (macOS 14+) |
| Image engine | Python 3.11+ |
| Array math | NumPy |
| JPEG/PNG/TIFF decode | Pillow |
| RAW decode | rawpy (LibRaw) |
| EXIF reading | exifread |
| Testing | pytest |

---

## Development Setup

### Python engine

```bash
# Create virtual environment and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Swift shell

Open `Stacker/Stacker.xcodeproj` in Xcode, then set the following env vars in the Run scheme:

| Variable | Value |
|----------|-------|
| `STACKER_ENGINE_DIR` | `$(SRCROOT)/../engine` |
| `STACKER_PYTHON` | `/usr/bin/python3` (or `which python3`) |

Press ⌘R to build and run.

### Quick dev launch (after first Xcode build)

```bash
./run_dev.sh
```

---

## Output Filename Format

```
startrails_<first_frame>-<last_frame>_<total_exposure>_<method>.<ext>
```

Examples:
```
startrails_IMG_0001-IMG_0120_60min_lighten.jpg
startrails_DSC01234-DSC01380_73min_comet.tif
startrails_A7RIII_0001-A7RIII_0240_2h_gapfill.png
startrails_IMG_0001-IMG_0050_unknown-exposure_average.png
```

---

## Project Layout

```
Stacker/                    ← repo root
├── README.md
├── PROGRESS.md             ← build progress tracker
├── requirements.txt        ← Python deps
├── engine/                 ← Python image engine
│   ├── models.py
│   ├── ipc.py
│   ├── loader.py
│   ├── pipeline.py
│   ├── exporter.py
│   ├── server.py
│   ├── backends/
│   │   ├── base.py
│   │   └── cpu.py
│   └── methods/
│       ├── lighten.py
│       ├── maximum.py
│       ├── average.py
│       ├── comet.py
│       └── gapfill.py
├── tests/                  ← pytest suite
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_ipc.py
│   ├── test_loader.py
│   ├── test_methods.py
│   ├── test_gapfill.py
│   ├── test_pipeline.py
│   └── test_exporter.py
├── Stacker/                ← Xcode project (Phase 2)
│   └── Stacker/
│       ├── StackerApp.swift
│       ├── EngineClient.swift
│       ├── IPCTypes.swift
│       ├── AppState.swift
│       └── Views/
├── docs/
│   └── superpowers/
│       ├── specs/          ← design spec
│       └── plans/          ← implementation plan
└── run_dev.sh              ← dev launch helper
```

---

## Future Work

- GPU backend (Metal compute shaders) — toggle grayed out until CPU is stable
- Batch processing — queue multiple folder/method combinations
- Timelapse export — numbered frame sequence for ffmpeg
- Interval gap detection — warn on missing frames by timestamp
- Foreground blending — composite best foreground with trail result
- Histogram display during stacking
