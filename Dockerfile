FROM ubuntu AS dev
WORKDIR /workspace
SHELL ["/bin/bash", "-c"]

# Setup neovim config in container
COPY kickstart.nvim/ /root/.config/nvim/

COPY packages.txt /tmp

# Download zellij terminal multiplexer into container
ADD https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz /tmp

# Use local region mirror for install packages
RUN sed -i 's|http://archive.ubuntu.com/ubuntu|http://mirrors.gbnetwork.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources && \
    apt update

# Install kickstart.nvim dependencies
RUN apt install -y git make unzip gcc ripgrep npm fzf neovim fish curl && \
    xargs -a /tmp/packages.txt apt install -y && \
    tar -xzf /tmp/zellij-x86_64-unknown-linux-musl.tar.gz -C /bin && \
    mkdir -p /root/.config/nvim

# Setup neovim
RUN git clone --filter=blob:none https://github.com/folke/lazy.nvim.git --branch=stable /lazy/lazy.nvim && nvim "+Lazy! install" +MasonToolsInstallSync +q!

# Start container with Zellij terminal multiplexer
CMD ["zellij", "options", "--default-shell", "fish"]

FROM dev AS dev-python
WORKDIR /workspace
SHELL ["/bin/bash", "-c"]

# Copy python module requirements into container
COPY requirements.txt /tmp

# Install kickstart.nvim and python dependencies
RUN apt install -y python3 python3-pip && \
    pip install -r /tmp/requirements.txt --break-system-packages

CMD ["zellij", "options", "--default-shell", "fish"]

FROM codercom/code-server AS coder
WORKDIR /home/coder/project
USER root

RUN code-server --install-extension vscodevim.vim && \
    code-server --install-extension pkief.material-icon-theme && \
    code-server --install-extension spacebox.monospace-idx-theme

COPY settings.json /root/.local/share/code-server/User/settings.json

COPY packages.txt /tmp

RUN apt update

RUN xargs -a /tmp/packages.txt apt install -y

ENTRYPOINT ["/usr/bin/entrypoint.sh", "--bind-addr", "0.0.0.0:8080", "--auth", "none", "."]

FROM coder AS coder-python

COPY requirements.txt /tmp

RUN apt install -y python3 python3-pip && \
    pip install -r /tmp/requirements.txt --no-cache-dir --break-system-packages

FROM python:3.12-slim AS prod

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Use local region mirror for install packages
RUN apt update

# Install Pytesseract library dependency
RUN apt install -y tesseract-ocr && \
    apt install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER root

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]