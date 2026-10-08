FROM deepnote/python:3.11

USER root

ARG CODE_SERVER_VERSION=4.140.0

ENV DEBIAN_FRONTEND=noninteractive \
    REMOTE_IDE_ROOT=/work/.remote-ide \
    REMOTE_IDE_PROJECTS=/work/projects \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/remote-ide:${PYTHONPATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    git-lfs \
    openssh-client \
    build-essential \
    gcc \
    g++ \
    gdb \
    make \
    cmake \
    pkg-config \
    jq \
    ripgrep \
    fd-find \
    tmux \
    nano \
    vim \
    unzip \
    zip \
    tree \
    htop \
    lsof \
    procps \
    openjdk-17-jdk-headless \
    maven \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && node --version \
    && npm --version

# Current Gradle release
ARG GRADLE_VERSION=9.8.1
RUN curl -fsSL https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip     -o /tmp/gradle.zip     && unzip -q /tmp/gradle.zip -d /opt     && ln -s /opt/gradle-${GRADLE_VERSION} /opt/gradle     && ln -s /opt/gradle/bin/gradle /usr/local/bin/gradle     && rm -f /tmp/gradle.zip     && gradle --version

# code-server (browser VS Code)
RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --version "${CODE_SERVER_VERSION}" \
    && code-server --version

RUN mkdir -p /opt/remote-ide /etc/jupyter/jupyter_server_config.d \
    /work/.remote-ide /work/projects \
    && chmod 1777 /work/.remote-ide /work/projects

COPY remote_ide_manager.py /opt/remote-ide/remote_ide_manager.py
COPY remote_ide_jupyter_extension.py /opt/remote-ide/remote_ide_jupyter_extension.py
COPY jupyter_server_config.d/remote_ide.py /etc/jupyter/jupyter_server_config.d/remote_ide.py

RUN chmod 755 /opt/remote-ide/remote_ide_manager.py

# Keep Deepnote's normal runtime behavior. The Jupyter Server extension is
# responsible for launching code-server in the background.
USER root
