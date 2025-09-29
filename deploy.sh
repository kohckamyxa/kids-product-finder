#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 {build|start}" >&2
  exit 1
fi

COMMAND=$1

install_chromium() {
  if command -v chromium-browser >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1; then
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    echo "Chromium is missing and apt-get is unavailable; set CHROME_BIN to a valid binary." >&2
    return 1
  fi

  echo "Installing Chromium for headless Selenium runs..."
  apt-get update
  apt-get install -y chromium-browser chromium-chromedriver || apt-get install -y chromium chromium-driver
}

case "$COMMAND" in
  build)
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    ;;
  start)
    install_chromium || true
    if command -v chromium-browser >/dev/null 2>&1; then
      export CHROME_BIN=${CHROME_BIN:-$(command -v chromium-browser)}
    elif command -v chromium >/dev/null 2>&1; then
      export CHROME_BIN=${CHROME_BIN:-$(command -v chromium)}
    fi
    exec gunicorn backend.app:app --bind "0.0.0.0:${PORT:-5000}" --timeout 120
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    exit 1
    ;;
esac
