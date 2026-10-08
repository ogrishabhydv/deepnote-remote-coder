#!/usr/bin/env bash
set -uo pipefail
EXT_DIR=/opt/remote-ide/bundled-extensions
mkdir -p "$EXT_DIR"
extensions=(
  ms-python.python ms-toolsai.jupyter llvm-vs-code-extensions.vscode-clangd ms-vscode.cmake-tools
  vscjava.vscode-java-pack golang.Go rust-lang.rust-analyzer REditorSupport.r
  dbaeumer.vscode-eslint esbenp.prettier-vscode redhat.vscode-yaml redhat.vscode-xml
  mtxr.sqltools mtxr.sqltools-driver-sqlite mtxr.sqltools-driver-pg mtxr.sqltools-driver-mysql
  qwtel.sqlite-viewer ritwickdey.LiveServer bradlc.vscode-tailwindcss eamodio.gitlens
  usernamehw.errorlens yzhang.markdown-all-in-one streetsidesoftware.code-spell-checker
  github.vscode-pull-request-github mikestead.dotenv
)
fail=0
for ext in "${extensions[@]}"; do
  if ! code-server --extensions-dir "$EXT_DIR" --install-extension "$ext" --force; then
    echo "WARNING: extension failed: $ext"
    fail=$((fail+1))
  fi
done
echo "Extension install failures: $fail"
# Open VSX availability can change, so failed optional extensions do not fail the whole build.
exit 0
