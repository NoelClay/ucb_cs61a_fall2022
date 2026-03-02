#!/bin/bash
# 새 PC에서 처음 실행 시 패키지 설치
# Usage: bash pipeline/setup.sh

USB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES_DIR="$USB_ROOT/pipeline/packages"

echo "[setup] USB_ROOT: $USB_ROOT"
echo "[setup] Installing packages to: $PACKAGES_DIR"
mkdir -p "$PACKAGES_DIR"

# 개발 패키지
pip install --target="$PACKAGES_DIR" --no-cache-dir \
    -r "$USB_ROOT/pipeline/requirements-dev.txt"

echo ""
echo "[setup] Done. Run scripts with: bash pipeline/run.sh <script.py>"
