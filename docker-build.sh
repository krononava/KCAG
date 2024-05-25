#!/bin/bash

cp -r $HOME/dotfiles/kickstart.nvim .
docker build --target $1 -t project .
rm -r kickstart.nvim
docker run -it -v .:/workspace project