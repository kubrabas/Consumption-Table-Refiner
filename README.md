# Consumption-Table-Refiner

## Start as a Mac app (recommended on macOS)

1. Clone the project:
   ```bash
   git clone https://github.com/kubrabas/Consumption-Table-Refiner.git
   ```
2. Double-click `install.command` in the project folder (only once). It adds **Consumption Table Refiner** to the Applications folder.
3. Start it like any other app: **command + space**, type "Consumption", press Enter. The app opens in the browser.

Good to know:
- The first start takes 1–2 minutes: it creates the Python environment `.venv_ctr` and installs the packages. Later starts take a few seconds.
- The app stops by itself about 1 minute after its last browser tab was closed. It is only reachable from your own computer.
- If the project folder is inside Desktop, Documents or Downloads, macOS asks once whether "Consumption Table Refiner" may access that folder. Click **Allow**:
  - Why it is needed: the app runs its code from the project folder. It reads the scripts and the Python environment `.venv_ctr` there, and saves the prepared tables there.
  - Why it is safe: the permission is only for this app, and the app only runs the code of this project. It is only reachable from your own computer, sends no usage statistics, and does not upload your files anywhere.
  - macOS only allows access to the whole folder (e.g. all of Desktop), not to a single subfolder. If you prefer not to give it, clone the project outside these folders (e.g. `~/Repositories`): then macOS does not ask. You can withdraw the permission at any time in System Settings → Privacy & Security → Files and Folders.
- It uses the Python of macOS (`/usr/bin/python3`). If it is missing, macOS offers to install the Command Line Tools.
- The app runs the code of the project folder, so after a `git pull` no new installation is needed. Run `install.command` again only if you move the folder.
- If the project was downloaded as a ZIP file instead of `git clone`, macOS may block `install.command` on the first double-click: System Settings → Privacy & Security → "Open Anyway".
- Log of the last start: `~/Library/Logs/Consumption Table Refiner/app.log`

## Run manually (macOS, Linux, Windows)

### 1) Clone and enter the project
```bash
git clone https://github.com/kubrabas/Consumption-Table-Refiner.git
cd Consumption-Table-Refiner
```

### 2) Create & activate a virtual environment
#### macOS / Linux
```bash
python3 -m venv .venv_ctr
source .venv_ctr/bin/activate
```
#### Windows (PowerShell)
```bash
python -m venv .venv_ctr
.\.venv_ctr\Scripts\Activate.ps1
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Start the Streamlit app
```bash
streamlit run app.py
```

## Update to a new version
```bash
cd Consumption-Table-Refiner
git pull
```
- **Mac app:** nothing else to do. The next start uses the new code and installs new packages by itself if `requirements.txt` changed. If the app is open, close its browser tab first; it stops after about a minute. If you installed the project before the Mac app existed, double-click `install.command` once.
- **Manual run:** activate the environment, run `pip install -r requirements.txt`, then `streamlit run app.py`.
