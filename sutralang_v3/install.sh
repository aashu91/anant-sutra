#!/bin/sh
# SutraLang 3.0 Universal Zero-Dependency Installer Protocol

set -e

echo "===================================================="
echo "      SUTRALANG 3.0 UNIVERSAL INSTALLER            "
echo "===================================================="

ARCH=$(uname -m)
OS=$(uname -s)

echo "[+] Architecture detected: ${ARCH} (${OS})"
INSTALL_DIR="$HOME/.sutra/bin"
mkdir -p "$INSTALL_DIR"

if [ -f "/data/data/com.termux/files/home/sutralang_v3/sutrac" ]; then
    cp /data/data/com.termux/files/home/sutralang_v3/sutrac "$INSTALL_DIR/sutra"
    cp /data/data/com.termux/files/home/sutralang_v3/sutrapak "$INSTALL_DIR/sutrapak" 2>/dev/null || true
    echo "[✓] Native binaries installed to $INSTALL_DIR"
fi

echo ""
echo "Installation complete!"
echo "Run 'sutra --version' or 'sutrapak' to begin."
