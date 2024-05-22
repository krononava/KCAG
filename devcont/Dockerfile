FROM ubuntu
WORKDIR /workspace

SHELL ["/bin/bash", "-c"]

# Install kickstart.nvim dependencies
RUN apt update
RUN apt install -y git make unzip gcc ripgrep xclip npm fzf neovim fish curl

# project dependencies
RUN apt install -y tesseract-ocr python3 python3-pip
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt --break-system-packages

ADD https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz /tmp

RUN tar -xzf /tmp/zellij-x86_64-unknown-linux-musl.tar.gz -C /bin

RUN mkdir -p /root/.config/nvim

CMD ["zellij", "options", "--default-shell", "fish"]
