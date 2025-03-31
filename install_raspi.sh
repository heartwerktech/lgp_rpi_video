#!/bin/bash

# Update and upgrade
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3-pip vlc

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install python-vlc==3.0.18121
pip3 install opencv-python
pip3 install numpy
pip3 install RPi.GPIO

echo "Installation complete!"
echo "You may need to configure the WQHD (2K) framebuffer as described in the README.md" 