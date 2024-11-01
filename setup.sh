#!/bin/bash

# Displaying initial information
echo "This has been tested and verified on a clean Ubuntu 22.04 LTS (Jammy Jellyfish)"
read -p "Do you have a this OS? (y/n): " CONTINUE

if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
    echo "Setup aborted. Exiting."
    exit 0
fi
echo "This script will set up your development environment by installing the following:"
echo "- Visual Studio Code"
echo "- Google Chrome"
echo "- GitHub Desktop"
echo "- DisplayLink driver (if available)"
echo "- Webots (if available)"
echo "- Python and necessary packages"
echo "- VS Code extensions for Python and C/C++"
echo "- TeX Live for LaTeX support"
echo ""
echo "Please ensure you have the following files ready in your Downloads folder:"
echo "- DisplayLink Synaptics APT Repository .deb file (from https://www.synaptics.com/products/displaylink-graphics/downloads/ubuntu)"
echo "- Webots 2023b .deb file (from https://cyberbotics.com/#download)"
echo ""
read -p "Do you want to continue with the setup? (y/n): " CONTINUE

if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
    echo "Setup aborted. Exiting."
    exit 0
fi

# Update package list
echo "Updating package list..."
sudo apt update

# INSTALLING VS CODE
echo "Installing Visual Studio Code..."
sudo snap install --classic code

# INSTALLING GOOGLE CHROME
CHROME_DEB="$HOME/Downloads/google-chrome-stable_current_amd64.deb"
if [ ! -f "$CHROME_DEB" ]; then
    echo "Downloading Google Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O "$CHROME_DEB"
fi
echo "Installing Google Chrome..."
sudo dpkg -i "$CHROME_DEB" || sudo apt --fix-broken install -y

# INSTALLING GITHUB DESKTOP
echo "Setting up GitHub Desktop package feed and installing GitHub Desktop..."
wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/shiftkey-packages.gpg > /dev/null
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/ubuntu/ any main" > /etc/apt/sources.list.d/shiftkey-packages.list'
sudo apt update
sudo apt install github-desktop -y

# INSTALLING DISPLAYLINK DRIVER
DISPLAYLINK_DEB="$HOME/Downloads/synaptics-repository-keyring.deb"
if [ -f "$DISPLAYLINK_DEB" ]; then
    echo "Installing DisplayLink driver for multi-display via USB..."
    sudo apt install "$DISPLAYLINK_DEB" -y
    sudo apt update
    sudo apt install displaylink-driver -y
else
    echo "DisplayLink .deb file not found in Downloads. Please download it from:"
    echo "https://www.synaptics.com/products/displaylink-graphics/downloads/ubuntu"
    echo "After downloading, place the file in the Downloads folder and rerun this script."
    exit 1
fi

# INSTALLING WEBOTS
WEBOTS_DEB="$HOME/Downloads/webots_2023b_amd64.deb"
if [ -f "$WEBOTS_DEB" ]; then
    echo "Installing Webots..."
    sudo apt install "$WEBOTS_DEB" -y
    export WEBOTS_HOME=/usr/local/webots
else
    echo "Webots .deb file not found in Downloads. Please download it from:"
    echo "https://cyberbotics.com/#download"
    echo "After downloading, place the file in the Downloads folder and rerun this script."
    exit 1
fi

# SETTING UP PYTHON AND DEPENDENCIES
echo "Checking Python installation and installing dependencies..."
sudo apt install python3 -y
sudo apt install python3-pip -y
pip install numpy pandas scipy matplotlib pyserial

# Installing VS Code extensions for Python and C/C++
echo "Installing VS Code Python and C/C++ extensions..."
code --install-extension ms-python.python
code --install-extension ms-vscode.cpptools

# INSTALLING TEX FOR LATEX IN PLOTS
echo "Installing LaTeX (TeX Live full) for plot rendering in Python..."
sudo apt-get install texlive-full -y

echo "Setup complete! Please restart your machine to apply all changes."
