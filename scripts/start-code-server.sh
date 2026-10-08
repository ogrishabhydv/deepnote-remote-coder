#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/go/bin:/opt/cargo/bin:/work/.remote-ide/go/bin:$PATH"

if [[ -x /compute-helpers/code/print-integration-env-vars.py ]]; then
  # Deepnote integrations are not automatically exported into terminal processes.
  # Evaluate the helper's assignments without printing them.
  set +u
  eval "$(/compute-helpers/code/print-integration-env-vars.py)"
  set -u
fi

exec python /opt/remote-ide/remote_ide_manager.py serve
