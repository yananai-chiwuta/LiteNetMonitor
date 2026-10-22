# Contributing

Issues and pull requests are welcome. Keep the app focused, lightweight, and usable across Windows, macOS, and Linux. The interface uses the Python standard library's Tkinter; avoid adding another UI toolkit.

## Set up

Use Python 3.11 or newer, create a virtual environment, and install the runtime dependency:

```sh
python -m venv .venv
python -m pip install -r requirements.txt
```

If working on optional tray behavior on Windows or Linux, also install `requirements-tray.txt`. Linux may require a distribution package for Tkinter, commonly `python3-tk`.

Run the app with `python LiteNetMonitor.pyw`. Before opening a pull request, check that modified Python files compile and run the tests with `python -m unittest discover -s tests -v`. Desktop integration tests skip if no graphical display is available.

## Pull requests

Describe the user-visible change and the platforms you exercised. Keep changes narrow, preserve existing settings where possible, and include tests for core behavior when practical. Do not claim a platform was tested unless you ran it there.

By submitting a contribution, you agree that it is offered under the repository's MIT license.
