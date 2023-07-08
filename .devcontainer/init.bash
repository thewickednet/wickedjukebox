#!/bin/bash

set -xe
echo 'export PATH=~/.local/bin:${PATH}' >> ~/.bashrc
source ~/.bashrc

export PATH=~/.local/bin:${PATH}

pip install -U pip
pip install pipx
pipx install fabric
pipx install pre-commit


[ -d env ] || python3 -m venv env
./env/bin/pip install -U pip
./env/bin/pip install -e ".[dev]"
./env/bin/wjb migrate

pre-commit install
