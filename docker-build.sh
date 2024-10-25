#!/bin/bash

if [[ $1 == *"coder"* ]]; then
    docker build --target $1 -t project .
    docker run -it -p 127.0.0.1:8080:8080 -v "$PWD:/home/coder/project" project
else
    cp -r $HOME/dotfiles/kickstart.nvim .
    docker build --target $1 -t project .
    rm -r kickstart.nvim
    docker run -it -v .:/workspace project
fi
