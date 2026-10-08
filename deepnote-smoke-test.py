from __future__ import annotations

import shutil
import socket
import subprocess
from pathlib import Path


def run(*args: str) -> str:
    return subprocess.check_output(
        args, text=True, stderr=subprocess.STDOUT
    ).strip()


def first_line(*args: str) -> str:
    return run(*args).splitlines()[0]


checks = [
    ("python", ("python", "--version")),
    ("java", ("java", "-version")),
    ("node", ("node", "--version")),
    ("npm", ("npm", "--version")),
    ("git", ("git", "--version")),
    ("gcc", ("gcc", "--version")),
    ("clang", ("clang", "--version")),
    ("cmake", ("cmake", "--version")),
    ("maven", ("mvn", "--version")),
    ("gradle", ("gradle", "--version")),
    ("go", ("/usr/local/go/bin/go", "version")),
    ("gofmt", ("/usr/local/go/bin/gofmt", "--help")),
    ("rustc", ("/opt/cargo/bin/rustc", "--version")),
    ("cargo", ("/opt/cargo/bin/cargo", "--version")),
    ("r", ("R", "--version")),
    ("php", ("php", "--version")),
    ("ruby", ("ruby", "--version")),
    ("code-server", ("code-server", "--version")),
]

for name, command in checks:
    print(f"{name}: {first_line(*command)}")

# Also verify that the user-facing command names resolve through PATH.
for command in ("go", "gofmt", "rustc", "cargo", "code-server"):
    resolved = shutil.which(command)
    assert resolved, f"{command} is not on PATH"
    print(f"{command} PATH: {resolved}")

assert Path("/work/projects").exists()
assert Path("/opt/remote-ide/remote_ide_manager.py").exists()

with socket.socket() as sock:
    sock.settimeout(0.5)
    listening = sock.connect_ex(("127.0.0.1", 8080)) == 0

assert listening, "code-server is not listening on 8080"
print("8080: listening")
