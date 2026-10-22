# Lite NetMonitor

A small desktop widget for watching network traffic. It uses Python, Tkinter, and psutil, with native window decorations on macOS and Linux and a compact borderless window on Windows.

## What it does

- Shows current download and upload rates, with a bounded one-minute graph.
- Displays received and sent totals for the current session, with a reset action.
- Supports midnight and paper themes, KiB/s or decimal bits/s, adapter selection, and an unavailable state when an adapter cannot be read.
- Lets you pause the display while traffic sampling continues.
- Saves the theme, units, selected adapter, topmost setting, sampling interval, and window position.
- Exports a CSV snapshot and copies the current speeds.
- Offers an optional system tray on Windows and Linux. macOS uses the regular window minimize behavior.
- On Windows, provides an optional startup toggle.

The app does not make network requests in the background. The explicit ping action contacts `1.1.1.1`.

## Run from source

Python 3.11 or newer is recommended. Tkinter is included with many Python installers; on Linux, install your distribution's Tk package if it is missing (often named `python3-tk`).

```sh
python -m venv .venv
```

Activate the environment, then install and run:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate` (use `python3` to create the environment if needed).

```sh
python -m pip install -r requirements.txt
python LiteNetMonitor.pyw
```

For optional tray support when running from source on Windows or Linux, run `python -m pip install -r requirements-tray.txt`. Tray availability depends on desktop environment support. On macOS, use the normal window controls. Compact packaged builds use regular minimize and omit tray libraries.

Right-click or use **•••** for settings and tools. **Space** pauses the display, **Ctrl/Cmd+C** copies speeds, **T** changes theme, and **Escape** minimizes. Drag the header to move the widget. Session totals reset when you quit, reset the session, or change adapters; they are not a monthly data meter. All-adapter totals may count VPN and virtual-interface traffic more than once; select your physical adapter for a clearer reading.

## Build status

GitHub Actions can build downloadable platform artifacts when manually run from the Actions tab. These are unsigned CI artifacts, not a published or signed release. The project has not yet verified these builds on real Windows, macOS, and Linux desktop sessions; Tk availability and tray behavior vary by platform.

## License

MIT. This permissive license allows reuse, modification, and redistribution while requiring preservation of copyright and license notices. See [MIT terms](https://choosealicense.com/licenses/mit/). Dependencies retain their own licenses: psutil uses BSD-3-Clause; optional pystray uses LGPL-3.0 and Pillow uses MIT-CMU. The compact build omits these tray extras.

## Project direction

The goal is a focused desktop monitor that stays small and easy to run. Future ideas include optional longer-term history and configurable data caps, if they can be added without making the widget cumbersome.
