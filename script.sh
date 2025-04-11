#!/bin/bash

# تعریف متغیرها
PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanel.git"
INSTALL_DIR="/opt/$PROJECT_NAME"
PYTHON_VERSION="python3"
PORT=${1:-5000} # پورت از آرگومان اول اسکریپت گرفته می‌شود (پیش‌فرض: 5000)
ADMIN_FILE="$INSTALL_DIR/admin.json"


read -p "Enter admin username: " ADMIN_USERNAME
read -p "Enter admin password: " ADMIN_PASSWORD
echo # برای ایجاد خط جدید بعد از ورودی رمز عبور

# 1. بررسی و نصب پایتون
echo "Checking for Python..."
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "Python not found. Installing Python..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
        elif [[ "$ID" == "centos" || "$ID" == "rhel" ]]; then
            sudo yum install -y python3 python3-pip python3-virtualenv
        else
            echo "Unsupported Linux distribution. Please install Python manually."
            exit 1
        fi
    else
        echo "Could not detect Linux distribution. Please install Python manually."
        exit 1
    fi
fi
echo "Python is installed."

# 2. بررسی و نصب Git
echo "Checking for Git..."
if ! command -v git &> /dev/null; then
    echo "Git not found. Installing Git..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
            sudo apt update
            sudo apt install -y git
        elif [[ "$ID" == "centos" || "$ID" == "rhel" ]]; then
            sudo yum install -y git
        else
            echo "Unsupported Linux distribution. Please install Git manually."
            exit 1
        fi
    else
        echo "Could not detect Linux distribution. Please install Git manually."
        exit 1
    fi
fi
echo "Git is installed."

# 3. کلون کردن پروژه از GitHub
echo "Cloning the project from GitHub..."
if [ -d "$INSTALL_DIR" ]; then
    echo "Project directory already exists. Updating the project..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo "Project cloned successfully."


# 5. ایجاد فایل admin.json و ذخیره اطلاعات مدیر
echo "Creating admin.json file..."
cat <<EOF > "$ADMIN_FILE"
{
  "username": "$ADMIN_USERNAME",
  "password": "$ADMIN_PASSWORD"
}
EOF
echo "Admin credentials saved to $ADMIN_FILE."

# 4. ایجاد محیط مجازی و نصب وابستگی‌ها
echo "Setting up virtual environment and installing dependencies..."
if [ ! -d "venv" ]; then
    $PYTHON_VERSION -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed."

# 5. ایجاد فایل سرویس systemd
SERVICE_NAME="$PROJECT_NAME.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "Creating systemd service file..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=$PROJECT_NAME
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/$PYTHON_VERSION app.py --port=$PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. راه‌اندازی سرویس
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "The project is now running on port $PORT."
echo "You can check the status of the service with: sudo systemctl status $SERVICE_NAME"