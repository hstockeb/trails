import json
import io
from engine.ipc import send_event, read_command


def test_send_event_writes_json_line(capsys):
    send_event("progress", {"frame": 5, "total": 100})
    captured = capsys.readouterr()
    msg = json.loads(captured.out.strip())
    assert msg == {"type": "progress", "payload": {"frame": 5, "total": 100}}


def test_read_command_parses_line():
    fake_stdin = io.TextIOWrapper(io.BytesIO(b'{"type":"cancel"}\n'))
    cmd = read_command(fake_stdin)
    assert cmd == {"type": "cancel"}


def test_read_command_returns_none_on_eof():
    fake_stdin = io.TextIOWrapper(io.BytesIO(b''))
    assert read_command(fake_stdin) is None
