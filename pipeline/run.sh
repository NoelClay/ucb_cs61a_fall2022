#!/bin/bash
# 파이프라인 스크립트 실행 래퍼
# Usage: bash pipeline/run.sh modules/01_download.py
# Usage: bash pipeline/run.sh control_tower.py

USB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES_DIR="$USB_ROOT/pipeline/packages"

export USB_ROOT
export PYTHONPATH="$PACKAGES_DIR:$USB_ROOT:$PYTHONPATH"
export PYTHONNOUSERSITE=1  # 홈 디렉토리 손상 패키지 무시
export PATH="$USB_ROOT/pipeline/bin:$PATH"

if [ -f "$USB_ROOT/.env" ]; then
    export $(grep -v '^#' "$USB_ROOT/.env" | xargs)
fi

echo "[run] USB_ROOT=$USB_ROOT"
python3 "$USB_ROOT/pipeline/$1" "${@:2}"
