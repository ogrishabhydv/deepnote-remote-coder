#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import secrets
import socket
import subprocess
from pathlib import Path

ROOT = Path(os.environ.get("REMOTE_IDE_ROOT", "/work/.remote-ide"))
PROJECTS = Path(os.environ.get("REMOTE_IDE_PROJECTS", "/work/projects"))
CONFIG = ROOT / "config.yaml"
PASSWORD_FILE = ROOT / "password.txt"
USER_DATA = ROOT / "user-data"
EXTENSIONS = ROOT / "extensions"
BUNDLED_EXTENSIONS = Path("/opt/remote-ide/bundled-extensions")
HOME = ROOT / "home"
LOG = ROOT / "code-server.log"
PID = ROOT / "code-server.pid"
PORT = int(os.environ.get("REMOTE_IDE_PORT", "8080"))
AUTH = os.environ.get("REMOTE_IDE_AUTH", "password").strip().lower()


def private_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o600)


def ensure_dirs() -> None:
    for p in (ROOT, PROJECTS, USER_DATA, EXTENSIONS, HOME,
              ROOT / "maven", ROOT / "gradle", ROOT / "pip-cache",
              ROOT / "npm-cache", ROOT / "go", ROOT / "go/bin", ROOT / "R/library"):
        p.mkdir(parents=True, exist_ok=True)


def get_password() -> str:
    value = os.environ.get("REMOTE_IDE_PASSWORD", "").strip()
    if value:
        private_write(PASSWORD_FILE, value + "\n")
        return value
    if PASSWORD_FILE.exists():
        value = PASSWORD_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value
    value = secrets.token_urlsafe(24)
    private_write(PASSWORD_FILE, value + "\n")
    return value


def copy_if_missing(src: Path, dst: Path) -> None:
    if not src.exists() or dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-a", str(src), str(dst)], check=True)


def seed_persistent_state() -> None:
    ensure_dirs()
    # Make the common ~/work path point to Deepnote's persistent /work location.
    home_work = Path("/root/work")
    try:
        if home_work.is_symlink() or home_work.exists():
            if home_work.is_symlink() and home_work.resolve() == Path("/work"):
                pass
            elif home_work.is_dir() and not home_work.is_symlink():
                # Do not delete user data; leave a real directory alone.
                pass
            else:
                home_work.unlink(missing_ok=True)
        if not home_work.exists():
            home_work.symlink_to("/work")
    except OSError:
        pass

    settings = USER_DATA / "User" / "settings.json"
    copy_if_missing(Path("/opt/remote-ide/vscode-settings.json"), settings)
    for src in BUNDLED_EXTENSIONS.iterdir() if BUNDLED_EXTENSIONS.exists() else []:
        copy_if_missing(src, EXTENSIONS / src.name)


def ensure_config() -> None:
    seed_persistent_state()
    auth = AUTH if AUTH in {"password", "none"} else "password"
    lines = [
        f"bind-addr: 0.0.0.0:{PORT}",
        f"auth: {auth}",
        "cert: false",
        "disable-telemetry: true",
        "disable-update-check: true",
        f"user-data-dir: {USER_DATA}",
        f"extensions-dir: {EXTENSIONS}",
    ]
    if auth == "password":
        lines.insert(2, f"password: {json.dumps(get_password())}")
    desired = "\n".join(lines) + "\n"
    if not CONFIG.exists() or CONFIG.read_text(encoding="utf-8") != desired:
        private_write(CONFIG, desired)


def is_listening() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        try:
            return s.connect_ex(("127.0.0.1", PORT)) == 0
        except OSError:
            return False


def serve() -> int:
    ensure_config()
    if is_listening():
        return 0

    env = os.environ.copy()
    env.update({
        "HOME": str(HOME),
        "MAVEN_USER_HOME": str(ROOT / "maven"),
        "GRADLE_USER_HOME": str(ROOT / "gradle"),
        "PIP_CACHE_DIR": str(ROOT / "pip-cache"),
        "NPM_CONFIG_CACHE": str(ROOT / "npm-cache"),
        "GOPATH": str(ROOT / "go"),
        "GOBIN": str(ROOT / "go/bin"),
        "GOMODCACHE": str(ROOT / "go/pkg/mod"),
        "R_LIBS_USER": str(ROOT / "R/library"),
        "CARGO_HOME": "/opt/cargo",
        "RUSTUP_HOME": "/opt/rustup",
        "PATH": f"/usr/local/go/bin:/opt/cargo/bin:{ROOT / 'go/bin'}:" + env.get("PATH", ""),
    })

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("ab", buffering=0) as log:
        proc = subprocess.Popen(
            ["code-server", "--config", str(CONFIG), "--bind-addr", f"0.0.0.0:{PORT}", "--disable-telemetry"],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECTS),
            env=env,
        )
    private_write(PID, str(proc.pid) + "\n")
    return int(proc.wait() or 0)


def status() -> int:
    ensure_config()
    print(f"port={PORT}")
    print(f"auth={AUTH}")
    print(f"listening={is_listening()}")
    print(f"projects={PROJECTS}")
    print(f"user_data={USER_DATA}")
    print(f"extensions={EXTENSIONS}")
    print(f"password_file={PASSWORD_FILE}")
    return 0


def main() -> int:
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "serve":
        return serve()
    if cmd == "status":
        return status()
    raise SystemExit("Usage: remote_ide_manager.py [serve|status]")


if __name__ == "__main__":
    raise SystemExit(main())
