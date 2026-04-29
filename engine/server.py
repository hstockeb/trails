#!/usr/bin/env python3
"""
Entry point for the Python engine subprocess.
Reads newline-delimited JSON commands from stdin.
Writes newline-delimited JSON events to stdout.
All logging goes to stderr.
"""

import sys

import numpy as np

from engine.exporter import export_result
from engine.ipc import read_command, send_event
from engine.loader import scan_folder
from engine.models import StackJob, StackOptions
from engine.pipeline import run_pipeline

_pending_result: np.ndarray | None = None
_pending_result_path: str | None = None


def handle_scan_folder(payload: dict) -> None:
    path = payload["path"]
    try:
        frames = scan_folder(path)
        send_event("scan_complete", [frame.to_dict() for frame in frames])
    except Exception as exc:
        send_event("error", {"message": str(exc)})


def handle_start_stack(payload: dict) -> None:
    global _pending_result
    global _pending_result_path

    try:
        job = StackJob.from_dict(payload)
        for event in run_pipeline(job):
            if event["type"] == "done":
                _pending_result_path = event["payload"].get("tmp_result_path")
                if _pending_result_path and _pending_result_path.endswith(".npy"):
                    _pending_result = np.load(_pending_result_path)
            send_event(event["type"], event["payload"])
    except Exception as exc:
        send_event("error", {"message": str(exc)})


def handle_export(payload: dict) -> None:
    global _pending_result

    if _pending_result is None:
        send_event("error", {"message": "No stacked result available. Run start_stack first."})
        return

    try:
        output_path = payload["output_path"]
        options = StackOptions(
            output_format=payload.get("format", "jpeg"),
            jpeg_quality=payload.get("quality", 85),
            resize=tuple(payload["resize"]) if payload.get("resize") else None,
            crop=tuple(payload["crop"]) if payload.get("crop") else None,
        )
        export_result(
            _pending_result,
            output_path,
            output_format=options.output_format,
            jpeg_quality=options.jpeg_quality,
            resize=options.resize,
            crop=options.crop,
        )
        send_event("export_done", {"output_path": output_path})
    except Exception as exc:
        send_event("error", {"message": str(exc)})


HANDLERS = {
    "scan_folder": handle_scan_folder,
    "start_stack": handle_start_stack,
    "export": handle_export,
}


def main() -> None:
    print("ready", file=sys.stderr, flush=True)
    while True:
        command = read_command()
        if command is None:
            break

        message_type = command.get("type")
        if message_type == "cancel":
            send_event("cancelled", {})
            continue

        handler = HANDLERS.get(message_type)
        if handler is None:
            send_event("error", {"message": f"Unknown command: {message_type}"})
            continue

        handler(command.get("payload", {}))


if __name__ == "__main__":
    main()
