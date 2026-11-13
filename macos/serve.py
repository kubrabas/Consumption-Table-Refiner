"""Runs the Consumption Table Refiner (app.py) with Streamlit and stops it when no browser tab is open any more.

Started by macos/launch.sh:  python macos/serve.py <port>
- The app only listens on localhost (not reachable from other computers) and sends no usage statistics.
- It stops by itself (like Ctrl+C) IDLE_STOP_SECONDS after its last browser tab was closed, or when no tab
  connected within STARTUP_GRACE_SECONDS after the start. A reload of the tab does not stop it.
"""

import os
import signal
import sys
import threading
import time
from pathlib import Path

IDLE_STOP_SECONDS = 60
STARTUP_GRACE_SECONDS = 300
CHECK_EVERY_SECONDS = 5
REPO_DIR = Path(__file__).resolve().parent.parent


def open_tabs():
    """Number of open browser tabs (active Streamlit sessions); None while the server is not up yet."""
    from streamlit.runtime import Runtime

    if not Runtime.exists():
        return None
    # _session_mgr is internal to Streamlit (checked with streamlit 1.50); if it disappears, the idle stop is switched off
    return Runtime.instance()._session_mgr.num_active_sessions()


def stop_when_idle():
    started = time.monotonic()
    last_open = None   # last check with at least one open tab
    previous = None
    while True:
        time.sleep(CHECK_EVERY_SECONDS)
        try:
            tabs = open_tabs()
        except Exception as error:   # Streamlit internals changed: keep the app running, without idle stop
            print(f"idle stop switched off: {error!r}", flush=True)
            return
        now = time.monotonic()
        if tabs != previous:
            print(f"open browser tabs: {tabs}", flush=True)
            previous = tabs
        if tabs:
            last_open = now
            continue
        idle_since = last_open if last_open is not None else started
        limit = IDLE_STOP_SECONDS if last_open is not None else STARTUP_GRACE_SECONDS
        if now - idle_since >= limit:
            print(f"no open browser tab for {int(now - idle_since)} s: stopping", flush=True)
            os.kill(os.getpid(), signal.SIGTERM)   # Streamlit shuts down cleanly on SIGTERM
            return


if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "8501"
    os.chdir(REPO_DIR)   # the app saves its output relative to the repository
    threading.Thread(target=stop_when_idle, daemon=True).start()

    from streamlit.web import cli

    sys.argv = [
        "streamlit", "run", str(REPO_DIR / "app.py"),
        "--server.port", port,
        "--server.address", "localhost",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    sys.exit(cli.main())
