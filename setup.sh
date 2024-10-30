#!/bin/bash



# Setting executable permissions for setup.sh...
# chmod +x path/setup.sh


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
