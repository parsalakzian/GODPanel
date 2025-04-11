#!/bin/bash

PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanel.git"
INSTALL_DIR="/opt/$PROJECT_NAME"
PYTHON_VERSION="3.12.8"
PYTHON_BIN="/usr/local/bin/python3.12"
ADMIN_FILE="$INSTALL_DIR/admin.json"

# 1. دریافت اطلاعات از کاربر
read -p "Enter admin username: " ADMIN_USERNAME
read -s -p "Enter admin password: " ADMIN_PASSWORD
echo
read -p "Enter the port number (default: 5000): " PORT
PORT=${PORT:-5000}

# 2. نصب Python 3.12.8 اگر موجود نباشد
echo "Checking for Python $PYTHON_VERSION..."
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Python $PYTHON_VERSION not found. Installing..."
    sudo apt update
    sudo apt install -y wget build-essential zlib1g-dev libncurses5-dev \
        libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev

    cd /tmp
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
    tar -xf Python-$PYTHON_VERSION.tgz
    cd Python-$PYTHON_VERSION
    ./configure --enable-optimizations
    make -j$(nproc)
    sudo make altinstall
else
    echo "Python $PYTHON_VERSION is already installed."
fi

# 3. بررسی و نصب Git
echo "Checking for Git..."
if ! command -v git &> /dev/null; then
    echo "Git not found. Installing..."
    sudo apt install -y git
fi

# 4. کلون پروژه
echo "Cloning the project from GitHub..."
if [ -d "$INSTALL_DIR" ]; then
    echo "Project directory already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 5. ذخیره admin.json
echo "Creating admin.json file..."
cat <<EOF > "$ADMIN_FILE"
{
  "username": "$ADMIN_USERNAME",
  "password": "$ADMIN_PASSWORD"
}
EOF

# 6. ساخت محیط مجازی با Python 3.12.8
echo "Creating virtual environment..."
$PYTHON_BIN -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. ساخت systemd service
SERVICE_NAME="$PROJECT_NAME.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=$PROJECT_NAME
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python app.py --port=$PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. فعال‌سازی سرویس
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "✅ The project is now running on port $PORT."
echo "📋 Check status: sudo systemctl status $SERVICE_NAME"
