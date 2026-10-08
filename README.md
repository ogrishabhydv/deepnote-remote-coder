# Deepnote Remote Coder v4

This image is intended for a Deepnote Free project and is built remotely by GitHub Actions.

Use the public image:

`leosword65/deepnote-remote-coder:v4`

Connect a Deepnote Environment Variables integration to the project and create:

`REMOTE_IDE_PASSWORD=<your chosen password>`

Do not put the real password in this repository or Docker Hub.

Keep all important code under `/work/projects/`. The image also stores code-server user data and extensions under `/work/.remote-ide/`. `/root/work` is made a symlink to `/work` where possible, so the common `~/work` path maps to persistent storage.

The image uses Deepnote Toolkit's `server.start_extra_servers` and `server.extra_servers` settings via `/etc/deepnote/config.toml` to launch code-server when the managed Deepnote runtime starts. It does not use the paid Init notebook and does not rely on Docker CMD/ENTRYPOINT.

The GitHub Actions workflow builds `linux/amd64`, starts the image with Deepnote Toolkit, verifies that code-server appears on port 8080 without a manual start command, verifies password protection, checks the toolchain, then pushes `:v4` and `:latest`.
