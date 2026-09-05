# Lite NetMonitor

A hyper-lightweight, borderless network monitor for Windows, built with Python and Tkinter. It sits on your desktop, monitors real-time upload/download speeds, and consumes virtually zero system resources.

## Features
* **System Tray Integration:** Runs quietly in the background.
* **Smart UI:** Borderless design with a modern 4px border radius.
* **Custom Themes:** Switch between Dark Hacker, Light Mode, and Matrix themes.
* **One-Click Copy:** Double-click the widget to instantly copy current speeds to your clipboard.
* **Network Tools:** Built-in latency (ping) checking, IP info, and NIC selection.
* **Auto-Start:** Optionally launch silently when Windows boots.

## Installation (Standalone .exe)
1. Go to the [Releases](../../releases) page.
2. Download `LiteNetMonitor.exe`.
3. Run the application (no installation or Python required).

## Development Setup
If you want to modify the source code:
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the script: `python LiteNetMonitor.pyw`

### Building the .exe
To compile your own executable, use PyInstaller:
```bash
py -m PyInstaller --noconsole --onefile --hidden-import pystray --hidden-import PIL LiteNetMonitor.pyw