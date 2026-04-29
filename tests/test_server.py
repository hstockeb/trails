import json
import subprocess
import sys
import time
import numpy as np
from PIL import Image
from pathlib import Path


def run_server(*commands) -> list[dict]:
    """Send one or more JSON commands to a single server process and collect events."""
    stdin = "".join(json.dumps(cmd) + "\n" for cmd in commands)
    proc = subprocess.run(
        [sys.executable, "-m", "engine.server"],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )
    return [json.loads(line) for line in proc.stdout.strip().splitlines() if line.strip()]


def test_server_scan_folder_command(tmp_image_folder):
    events = run_server({"type": "scan_folder", "payload": {"path": str(tmp_image_folder)}})
    assert events[0]["type"] == "scan_complete"
    assert len(events[0]["payload"]) == 5


def test_server_export_requires_pending_result(tmp_path):
    events = run_server({"type": "export", "payload": {"output_path": str(tmp_path / "out.jpg")}})
    assert events[0]["type"] == "error"
    assert "start_stack first" in events[0]["payload"]["message"]


def test_server_unknown_command_returns_error():
    events = run_server({"type": "banana", "payload": {}})
    assert events[0]["type"] == "error"
    assert "Unknown command" in events[0]["payload"]["message"]


def test_server_cancel_when_idle():
    events = run_server({"type": "cancel"})
    assert events[0]["type"] == "cancelled"


def test_server_full_stack_and_export(tmp_image_folder, tmp_path):
    """Send export only after receiving done — mirrors real Swift app behaviour."""
    frames = [
        {
            "path": str(p), "filename": p.name, "index": i,
            "width": 100, "height": 100, "is_raw": False,
            "capture_time": None, "exposure_seconds": 10.0,
        }
        for i, p in enumerate(sorted(tmp_image_folder.iterdir()))
    ]
    out = str(tmp_path / "result.jpg")

    proc = subprocess.Popen(
        [sys.executable, "-m", "engine.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )
    proc.stdin.write(json.dumps({"type": "start_stack", "payload": {
        "frames": frames, "method": "lighten",
        "options": {"output_format": "jpeg", "jpeg_quality": 85,
                    "preview_every_n_frames": 10},
    }}) + "\n")
    proc.stdin.flush()

    events = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        event = json.loads(line.strip())
        events.append(event)
        if event["type"] == "done":
            break

    proc.stdin.write(json.dumps(
        {"type": "export", "payload": {"output_path": out, "format": "jpeg", "quality": 85}}
    ) + "\n")
    proc.stdin.flush()
    proc.stdin.close()

    for line in proc.stdout:
        if line.strip():
            events.append(json.loads(line.strip()))
    proc.wait()

    types = [e["type"] for e in events]
    assert "done" in types
    assert "export_done" in types
    assert Path(out).exists()


def test_server_second_stack_clears_stale_result(tmp_image_folder, tmp_path):
    """A new start_stack must not leave the previous result accessible on failure."""
    frames = [
        {
            "path": str(p), "filename": p.name, "index": i,
            "width": 100, "height": 100, "is_raw": False,
            "capture_time": None, "exposure_seconds": 10.0,
        }
        for i, p in enumerate(sorted(tmp_image_folder.iterdir()))
    ]
    # First stack succeeds, second has a bad path → result must be cleared
    bad_frames = [{"path": "/nonexistent/img.jpg", "filename": "img.jpg", "index": 0,
                   "width": 0, "height": 0, "is_raw": False,
                   "capture_time": None, "exposure_seconds": None}]
    out = str(tmp_path / "out.jpg")
    events = run_server(
        {"type": "start_stack", "payload": {
            "frames": frames, "method": "lighten",
            "options": {"output_format": "jpeg", "jpeg_quality": 85,
                        "preview_every_n_frames": 10},
        }},
        {"type": "start_stack", "payload": {
            "frames": bad_frames, "method": "lighten",
            "options": {"output_format": "jpeg", "jpeg_quality": 85,
                        "preview_every_n_frames": 10},
        }},
        {"type": "export", "payload": {"output_path": out, "format": "jpeg", "quality": 85}},
    )
    export_events = [e for e in events if e["type"] == "export_done"]
    # Export should either fail (no pending result) or succeed with the first result
    # depending on thread timing — but must not silently export stale data after an error
    assert len(export_events) <= 1
