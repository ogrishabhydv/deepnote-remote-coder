from __future__ import annotations

import os
import subprocess
import threading


def _start_remote_ide() -> None:
    manager = "/opt/remote-ide/remote_ide_manager.py"
    try:
        subprocess.Popen(
            ["python", manager, "start"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=os.environ.copy(),
        )
    except Exception:
        # Do not break Deepnote/Jupyter if the optional remote IDE fails.
        pass


def _jupyter_server_extension_points():
    return [{"module": "remote_ide_jupyter_extension"}]


def _load_jupyter_server_extension(serverapp):
    threading.Thread(target=_start_remote_ide, daemon=True).start()


# Backwards-compatible Jupyter Server extension API.
load_jupyter_server_extension = _load_jupyter_server_extension
