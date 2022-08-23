#!/bin/sh

# Requires the package PyInstaller to be installed.

# run the build script for macos
python3 -m PyInstaller --onefile main.py

# copy in our asset folders
cp -rfv ships dist/
cp -rfv sounds dist/
cp -rfv sprites dist/

zip -r macos.zip dist
