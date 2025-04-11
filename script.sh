#!/bin/bash

PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanel.git"
INSTALL_DIR="$HOME/$PROJECT_NAME"
PYTHON_VERSION="3.12.8"
ADMIN_FILE="$INSTALL_DIR/admin.json"
ENV_NAME="$PROJECT_NAME-env"

# 1. گرفتن اطلاعات از کاربر
read -p "Enter admin username: " ADMIN_USERNAME
read -p "Enter admin password: " ADMIN_PASSWORD
echo
read -p "Enter the port number (default: 5000): " PORT
PORT=${PORT:-5000}


sudo systemctl stop "$PROJECT_NAME"

# 2. نصب pyenv اگر موجود نیست
if ! command -v pyenv &>/dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    SHELL_RC="$HOME/.bashrc"
    if [[ $SHELL == *zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    echo -e '\n# pyenv setup' >> $SHELL_RC
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> $SHELL_RC
    echo 'eval "$(pyenv init -)"' >> $SHELL_RC
    echo 'eval "$(pyenv virtualenv-init -)"' >> $SHELL_RC
fi

# بارگذاری pyenv برای همین ترمینال
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 3. نصب پایتون 3.12.8 با pyenv
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
    echo "Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install $PYTHON_VERSION
fi

# 4. کلون پروژه
if [ -d "$INSTALL_DIR" ]; then
    echo "Project exists. Pulling latest..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 5. ساخت محیط مجازی با pyenv
if ! pyenv virtualenvs --bare | grep -q "^$ENV_NAME$"; then
    pyenv virtualenv $PYTHON_VERSION $ENV_NAME
fi

cd "$INSTALL_DIR"
pyenv local $ENV_NAME
pip install --upgrade pip
pip install -r requirements.txt

# 6. ذخیره admin.json
cat <<EOF > "$ADMIN_FILE"
{
  "username": "$ADMIN_USERNAME",
  "password": "$ADMIN_PASSWORD"
}
EOF

# 7. ساخت فایل سرویس systemd
SERVICE_FILE="/etc/systemd/system/$PROJECT_NAME.service"
echo "Creating systemd service file at $SERVICE_FILE..."

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=$PROJECT_NAME
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$HOME/.pyenv/versions/$ENV_NAME/bin/python $INSTALL_DIR/app.py --port=$PORT
Restart=always
Environment=PYENV_VERSION=$ENV_NAME
Environment=PATH=$HOME/.pyenv/versions/$ENV_NAME/bin:$PATH
Environment=PORT=$PORT

[Install]
WantedBy=multi-user.target
EOF

# 8. فعال‌سازی و اجرای سرویس
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable "$PROJECT_NAME"
sudo systemctl restart "$PROJECT_NAME"

echo "✅ Setup and service complete."
echo "▶ Your project is running on port $PORT"
echo "🔍 Check status with: sudo systemctl status $PROJECT_NAME"
