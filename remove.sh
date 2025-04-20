#!/bin/bash

set -e

PROJECT_NAME="GODPanel"
GITHUB_REPO="https://github.com/parsalakzian/GODPanel.git"
INSTALL_DIR="/root/$PROJECT_NAME"
PYTHON_VERSION="3.12.8"
ENV_NAME="$PROJECT_NAME-env"
ADMIN_FILE="$INSTALL_DIR/admin.json"
SERVICE_FILE="/etc/systemd/system/$PROJECT_NAME.service"



# توقف سرویس اگر وجود دارد
if systemctl list-units --full -all | grep -q "$PROJECT_NAME.service"; then
    echo "Stopping existing service..."
    systemctl stop "$PROJECT_NAME.service"
fi

sudo rm -r "$INSTALL_DIR"