FROM deepnote/python:3.11-datascience

USER root

ARG CODE_SERVER_VERSION=4.140.0
ARG GRADLE_VERSION=9.8.1
ARG GO_VERSION=1.27.1

ENV DEBIAN_FRONTEND=noninteractive \
    REMOTE_IDE_ROOT=/work/.remote-ide \
    REMOTE_IDE_PROJECTS=/work/projects \
    REMOTE_IDE_PORT=8080 \
    REMOTE_IDE_AUTH=password \
    REMOTE_IDE_FIRST_FOLDER=/work/projects \
    MAVEN_USER_HOME=/work/.remote-ide/maven \
    GRADLE_USER_HOME=/work/.remote-ide/gradle \
    PIP_CACHE_DIR=/work/.remote-ide/pip-cache \
    NPM_CONFIG_CACHE=/work/.remote-ide/npm-cache \
    GOPATH=/work/.remote-ide/go \
    GOMODCACHE=/work/.remote-ide/go/pkg/mod \
    R_LIBS_USER=/work/.remote-ide/R/library \
    PATH=/usr/local/go/bin:/opt/cargo/bin:/work/.remote-ide/go/bin:${PATH} \
    PYTHONUNBUFFERED=1

# Deepnote Toolkit config: start our extra server automatically when its managed
# runtime starts. This uses the documented server.extra_servers configuration.
RUN mkdir -p /etc/deepnote && cat > /etc/deepnote/config.toml <<'TOML'
[server]
start_extra_servers = true
extra_servers = ["bash -lc /opt/remote-ide/start-code-server.sh"]
TOML

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget \
    git git-lfs openssh-client \
    build-essential gcc g++ clang gdb lldb make cmake ninja-build pkg-config \
    jq ripgrep fd-find tmux nano vim unzip zip tree htop lsof procps shellcheck zsh \
    sqlite3 libsqlite3-dev postgresql-client mariadb-client redis-tools \
    openjdk-17-jdk-headless maven \
    php-cli php-curl php-mbstring php-xml php-zip composer \
    ruby-full r-base r-base-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g typescript tsx ts-node eslint prettier pnpm yarn

RUN curl -fsSL https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -o /tmp/gradle.zip \
    && unzip -q /tmp/gradle.zip -d /opt \
    && ln -s /opt/gradle-${GRADLE_VERSION} /opt/gradle \
    && ln -s /opt/gradle/bin/gradle /usr/local/bin/gradle \
    && rm -f /tmp/gradle.zip

RUN curl -fsSL https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -o /tmp/go.tar.gz \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm -f /tmp/go.tar.gz \
    && GOBIN=/usr/local/bin go install golang.org/x/tools/gopls@latest \
    && GOBIN=/usr/local/bin go install github.com/go-delve/delve/cmd/dlv@latest

ENV RUSTUP_HOME=/opt/rustup CARGO_HOME=/opt/cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile default \
    && /opt/cargo/bin/rustup component add rust-analyzer rust-src clippy rustfmt

RUN python -m pip install --no-cache-dir \
    -c https://tk.deepnote.com/constraints3.11.txt \
    duckdb polars openpyxl xlrd pyxlsb pyreadstat \
    xgboost lightgbm catboost opencv-python-headless \
    networkx statsmodels plotly altair bokeh dask \
    fastapi "uvicorn[standard]" flask django gunicorn sqlalchemy alembic \
    pydantic-settings python-dotenv httpx beautifulsoup4 lxml redis \
    pytest pytest-cov ruff black isort mypy pre-commit nbconvert jupytext \
    sympy rich typer transformers datasets sentence-transformers streamlit gradio uv pip-tools

RUN mkdir -p /opt/R/site-library \
    && Rscript -e 'install.packages(c("languageserver","httpgd","jsonlite","data.table"), repos="https://cloud.r-project.org", lib="/opt/R/site-library")'
ENV R_LIBS_SITE=/opt/R/site-library

RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --version "${CODE_SERVER_VERSION}" \
    && code-server --version

RUN mkdir -p /opt/remote-ide/bundled-extensions /work/.remote-ide /work/projects

COPY scripts/remote_ide_manager.py /opt/remote-ide/remote_ide_manager.py
COPY scripts/start-code-server.sh /opt/remote-ide/start-code-server.sh
COPY scripts/install-vscode-extensions.sh /opt/remote-ide/install-vscode-extensions.sh
COPY scripts/vscode-settings.json /opt/remote-ide/vscode-settings.json

RUN chmod 755 /opt/remote-ide/*.sh /opt/remote-ide/remote_ide_manager.py \
    && python -m py_compile /opt/remote-ide/remote_ide_manager.py \
    && /opt/remote-ide/install-vscode-extensions.sh

USER root
