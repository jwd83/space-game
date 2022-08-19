#!/bin/sh

# Requires the package PyInstaller to be installed.

# run the build script for macos
python3 -m PyInstaller --onefile main.py

# copy in the ships folder to the dist folder
cp -rfv ships dist/

# copy in the sounds folder to the dist folder
cp -rfv sounds dist/

# copy in the music folder to the dist folder
cp -rfv music dist/


zip -r macos.zip dist