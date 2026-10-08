#!/usr/bin/env python3
from __future__ import annotations

import os
import secrets
import signal
import socket
import subprocess
import time
from pathlib import Path

ROOT = Path(os.environ.get("REMOTE_IDE_ROOT", "/work/.remote-ide"))
PROJECTS = Path(os.environ.get("REMOTE_IDE_PROJECTS", "/work/projects"))
CONFIG = ROOT / "config.yaml"
PASSWORD = ROOT / "password.txt"
LOG = ROOT / "code-server.log"
PID = ROOT / "code-server.pid"
PORT = int(os.environ.get("REMOTE_IDE_PORT", "8080"))


def _write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o600)


def ensure_config() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    PROJECTS.mkdir(parents=True, exist_ok=True)
    if not PASSWORD.exists():
        _write_private(PASSWORD, secrets.token_urlsafe(24) + "\n")
    password = PASSWORD.read_text(encoding="utf-8").strip()
    if not password:
        raise RuntimeError(f"{PASSWORD} is empty")

    if not CONFIG.exists():
        _write_private(
            CONFIG,
            "\n".join(
                [
                    f"bind-addr: 0.0.0.0:{PORT}",
                    "auth: password",
                    f"password: {password}",
                    "cert: false",
                    f"user-data-dir: {ROOT / 'user-data'}",
                    f"extensions-dir: {ROOT / 'extensions'}",
                    "disable-telemetry: true",
                ]
            )
            + "\n",
        )


def is_listening() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        try:
            return s.connect_ex(("127.0.0.1", PORT)) == 0
        except OSError:
            return False


def pid_is_running() -> bool:
    if not PID.exists():
        return False
    try:
        pid = int(PID.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        return False


def start() -> int:
    ensure_config()
    if is_listening():
        return 0

    ROOT.joinpath("user-data").mkdir(parents=True, exist_ok=True)
    ROOT.joinpath("extensions").mkdir(parents=True, exist_ok=True)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("ab", buffering=0) as log:
        proc = subprocess.Popen(
            [
                "code-server",
                "--config",
                str(CONFIG),
                "--bind-addr",
                f"0.0.0.0:{PORT}",
                "/work",
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd="/work",
        )
    _write_private(PID, str(proc.pid) + "\n")

    deadline = time.time() + 20
    while time.time() < deadline:
        if is_listening():
            return 0
        if proc.poll() is not None:
            return proc.returncode or 1
        time.sleep(0.25)

    return 1


def stop() -> int:
    if not PID.exists():
        return 0
    try:
        pid = int(PID.read_text().strip())
        os.kill(pid, signal.SIGTERM)
    except (ValueError, ProcessLookupError, PermissionError):
        pass
    try:
        PID.unlink()
    except FileNotFoundError:
        pass
    return 0


def status() -> int:
    ensure_config()
    print(f"port={PORT}")
    print(f"listening={is_listening()}")
    print(f"pid_running={pid_is_running()}")
    print(f"password_file={PASSWORD}")
    print(f"config_file={CONFIG}")
    print(f"projects={PROJECTS}")
    return 0


def main() -> int:
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "start":
        return start()
    if cmd == "stop":
        return stop()
    if cmd == "status":
        return status()
    raise SystemExit(f"Usage: {sys.argv[0]} [start|stop|status]")


if __name__ == "__main__":
    raise SystemExit(main())
