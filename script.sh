#!/bin/bash

set -e

PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanelCode.git"
INSTALL_DIR="/root/$PROJECT_NAME"
PYTHON_VERSION="3.12.8"
ENV_NAME="$PROJECT_NAME-env"
ADMIN_FILE="$INSTALL_DIR/admin.json"
SERVICE_FILE="/etc/systemd/system/$PROJECT_NAME.service"

# گرفتن اطلاعات از کاربر (همیشه)
read -p "Enter admin username: " ADMIN_USERNAME
read -s -p "Enter admin password: " ADMIN_PASSWORD
echo
read -p "Enter the port number (default: 5050): " PORT
PORT=${PORT:-5050}

# نصب pyenv در صورت نیاز
if ! command -v pyenv &>/dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash

    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
else
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
fi

# نصب نسخه پایتون
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
    pyenv install $PYTHON_VERSION
fi

# ساخت یا اطمینان از محیط مجازی
if ! pyenv virtualenvs --bare | grep -q "^$ENV_NAME$"; then
    pyenv virtualenv $PYTHON_VERSION $ENV_NAME
fi

# توقف سرویس اگر وجود دارد
if systemctl list-units --full -all | grep -q "$PROJECT_NAME.service"; then
    echo "Stopping existing service..."
    systemctl stop "$PROJECT_NAME.service"
fi

# کلون یا آپدیت پروژه
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating project..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning project..."
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# فعال‌سازی محیط و نصب وابستگی‌ها
cd "$INSTALL_DIR"
pyenv local $ENV_NAME
pip install --upgrade pip
pip install -r requirements.txt

# بروزرسانی admin.json
cat <<EOF > "$ADMIN_FILE"
{
  "username": "$ADMIN_USERNAME",
  "password": "$ADMIN_PASSWORD",
  "port": $PORT
}
EOF

# ساختن فایل systemd
echo "Creating systemd service..."
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=$PROJECT_NAME
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/root/.pyenv/versions/$ENV_NAME/bin/python app.py --port=$PORT
Restart=always
Environment=PORT=$PORT

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی سرویس
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable "$PROJECT_NAME.service"
systemctl start "$PROJECT_NAME.service"

echo "✅ $PROJECT_NAME is now running on port $PORT."