# Deepnote Remote Coder

A Deepnote Free-friendly remote development image:

- Deepnote's `deepnote/python:3.11` base
- code-server (VS Code in the browser)
- Python 3.11
- Java 21 + Maven + Gradle
- Node.js 22 + npm
- GCC/G++ + CMake + GDB
- Git, ripgrep, fd, jq, tmux, unzip/zip
- Persistent code-server settings/extensions under `/work/.remote-ide`
- A Python manager
- A Jupyter Server extension that attempts to start code-server automatically when Deepnote starts its Jupyter server

## Important Deepnote limitation

Deepnote Free recreates the runtime environment. Files under `/work` persist, but ad-hoc OS installs do not.

Use this as a **public Docker image** in Deepnote Free. Deepnote documents public Docker images as available on Free, and custom Dockerfile builds inside Deepnote as Team/Enterprise only.

## Build on an M-series Mac

Deepnote requires `linux/amd64` for custom environments:

```bash
docker buildx build \
  --platform linux/amd64 \
  -t YOUR_DOCKERHUB_USERNAME/deepnote-remote-coder:1.0 \
  --push .
```

Then in Deepnote:

1. Environment -> Hosted docker image / custom environment.
2. Enter the public image:
   `YOUR_DOCKERHUB_USERNAME/deepnote-remote-coder:1.0`
3. Enable Incoming connections for the project.
4. Start the machine.
5. Open the Deepnote-provided incoming-connections URL.

## First-time password

On the first automatic start, the manager creates:

```text
/work/.remote-ide/password.txt
/work/.remote-ide/config.yaml
```

The password is random and is never stored in the Docker image.

Open the password file once from the Deepnote Files/Terminal area and give the password to your brother. Do not publish the password or commit `/work/.remote-ide/config.yaml` to Git.

## Persistent files

Keep projects in:

```text
/work/projects/
```

The code-server user data and extensions are also placed under:

```text
/work/.remote-ide/
```

## Manual fallback

If the automatic Jupyter-extension startup does not happen in your Deepnote environment, run:

```bash
python /opt/remote-ide/remote_ide_manager.py start
```

Then open the project's incoming-connections URL.

## Security

Deepnote says incoming connections expose port 8080 to the internet. Never run code-server with `auth: none` on a public endpoint. This image keeps password authentication enabled.
