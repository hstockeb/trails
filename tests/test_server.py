import json
import subprocess
import sys


def test_server_scan_folder_command(tmp_image_folder):
    proc = subprocess.run(
        [sys.executable, "-m", "engine.server"],
        input=json.dumps({"type": "scan_folder", "payload": {"path": str(tmp_image_folder)}}) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0
    event = json.loads(proc.stdout.strip().splitlines()[0])
    assert event["type"] == "scan_complete"
    assert len(event["payload"]) == 5


def test_server_export_requires_pending_result(tmp_path):
    proc = subprocess.run(
        [sys.executable, "-m", "engine.server"],
        input=json.dumps(
            {
                "type": "export",
                "payload": {"output_path": str(tmp_path / "out.jpg")},
            }
        )
        + "\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0
    event = json.loads(proc.stdout.strip().splitlines()[0])
    assert event["type"] == "error"
    assert "start_stack first" in event["payload"]["message"]
