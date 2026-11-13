#!/bin/bash
# Starts the Consumption Table Refiner in the background and opens it in the browser.
# Started by "Consumption Table Refiner.app" (created by install.command); can also be run directly.
# - First start: creates the virtual environment .venv_ctr with the macOS Python (/usr/bin/python3) and installs
#   requirements.txt. Later starts install again only when requirements.txt has changed.
# - If the app is already running: only opens it in the browser.
# - The app stops by itself about 1 minute after its last browser tab was closed (macos/serve.py).
# Log of the last start: ~/Library/Logs/Consumption Table Refiner/app.log

set -u

APP_NAME="Consumption Table Refiner"
PORT=8517
URL="http://localhost:$PORT"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/.venv_ctr"
PYTHON=/usr/bin/python3
LOG_DIR="$HOME/Library/Logs/$APP_NAME"
LOG_FILE="$LOG_DIR/app.log"

notify() {
  /usr/bin/osascript -e "display notification \"$1\" with title \"$APP_NAME\"" >/dev/null 2>&1 || true
}

fail() {
  echo "ERROR: $1"
  /usr/bin/osascript -e "display alert \"$APP_NAME could not start\" message \"$1 The log opens now.\"" >/dev/null 2>&1 || true
  /usr/bin/open "$LOG_FILE"
  exit 1
}

is_running() {
  [ "$(/usr/bin/curl -s --max-time 2 "$URL/_stcore/health")" = "ok" ]
}

if is_running; then
  /usr/bin/open "$URL"
  exit 0
fi

mkdir -p "$LOG_DIR"
exec >"$LOG_FILE" 2>&1
echo "$(date '+%Y-%m-%d %H:%M:%S') start from $REPO_DIR"

# virtual environment: (re)install when it is missing or requirements.txt has changed
requirements_hash="$(/usr/bin/shasum -a 256 "$REPO_DIR/requirements.txt" | cut -d ' ' -f 1)"
marker="$VENV_DIR/.requirements.sha256"
if [ ! -x "$VENV_DIR/bin/python" ] || [ "$(cat "$marker" 2>/dev/null)" != "$requirements_hash" ]; then
  notify "Installing packages, this takes 1-2 minutes (only on the first start or after an update)."
  if [ ! -x "$VENV_DIR/bin/python" ]; then
    "$PYTHON" -m venv "$VENV_DIR" || fail "Could not create the Python environment."
  fi
  "$VENV_DIR/bin/python" -m pip install --upgrade pip || fail "Could not update pip."
  "$VENV_DIR/bin/python" -m pip install -r "$REPO_DIR/requirements.txt" || fail "Could not install the packages."
  echo "$requirements_hash" >"$marker"
fi

# start the app in the background, independent of this launcher, and open it once it answers
cd "$REPO_DIR" || fail "Repository folder not found: $REPO_DIR"
nohup "$VENV_DIR/bin/python" "$REPO_DIR/macos/serve.py" "$PORT" </dev/null &
server_pid=$!
for _ in $(seq 1 60); do
  if is_running; then
    /usr/bin/open "$URL"
    exit 0
  fi
  kill -0 "$server_pid" 2>/dev/null || fail "The app stopped during the start."
  sleep 1
done
fail "The app did not answer within 60 seconds."
