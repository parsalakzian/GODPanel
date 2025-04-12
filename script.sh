#!/bin/bash

PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanel.git"
INSTALL_DIR="/root/$PROJECT_NAME"
PYTHON_VERSION="3.12.8"
ENV_NAME="$PROJECT_NAME-env"
ADMIN_FILE="$INSTALL_DIR/admin.json"
SERVICE_FILE="/etc/systemd/system/$PROJECT_NAME.service"

# 1. گرفتن اطلاعات از کاربر
read -p "Enter admin username: " ADMIN_USERNAME
read -s -p "Enter admin password: " ADMIN_PASSWORD
echo
read -p "Enter the port number (default: 5050): " PORT
PORT=${PORT:-5050}

# 2. نصب pyenv اگر نصب نیست
if ! command -v pyenv &>/dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash

    echo 'export PATH="/root/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
fi

# بارگذاری pyenv در همین ترمینال
export PATH="/root/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 3. نصب پایتون موردنظر با pyenv
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
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

# 5. ساخت محیط مجازی
if ! pyenv virtualenvs --bare | grep -q "^$ENV_NAME$"; then
    pyenv virtualenv $PYTHON_VERSION $ENV_NAME
fi

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
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=GODPanel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/bin/bash -c 'export PATH="/root/.pyenv/bin:\$PATH"; eval "\$(pyenv init -)"; eval "\$(pyenv virtualenv-init -)"; pyenv activate $ENV_NAME; python app.py --port=$PORT'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. فعال‌سازی سرویس
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable $PROJECT_NAME.service
systemctl restart $PROJECT_NAME.service

echo "✅ GODPanel نصب و اجرا شد. برای مشاهده وضعیت:"
echo "  systemctl status $PROJECT_NAME.service"