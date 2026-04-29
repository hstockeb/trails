import json
import sys
from typing import Any


def send_event(event_type: str, payload: Any = None) -> None:
    msg = {"type": event_type, "payload": payload}
    print(json.dumps(msg), flush=True)


def read_command(stdin=None) -> dict | None:
    if stdin is None:
        stdin = sys.stdin
    while True:
        line = stdin.readline()
        if not line:
            return None
        stripped = line.strip()
        if stripped:
            return json.loads(stripped)
