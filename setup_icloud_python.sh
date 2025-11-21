#!/bin/bash

# Create virtual env in a non-synced directory
python3 -m venv .venv.nosync

# Create a symlink for easier access (optional, but iCloud might sync the link)
ln -s .venv.nosync .venv

# Activate
source .venv.nosync/bin/activate

# Install requirements
pip install -r requirements.txt

# Install playwright browsers
playwright install chromium

echo "Setup complete. To activate: source .venv.nosync/bin/activate"
