LiteNetMonitor 1.1.0 brings a compact, polished network widget to Windows, macOS, and Linux.

- Midnight and paper themes, a one-minute traffic graph, and separate download/upload readings.
- Session totals, CSV snapshots, copy speeds, keyboard shortcuts, and saved preferences.
- Adapter selection with safe handling of disappearing or newly added interfaces.
- A small runtime dependency set: Python, Tkinter, and psutil. No background requests or telemetry; ping only runs when requested.
- Version metadata in the app, Windows executable properties, and macOS app bundle.

Download the archive for your system, extract it, and launch LiteNetMonitor. Python is not required for these downloads. Each archive includes the README, changelog, version, and license notices. Verify downloads against `SHA256SUMS.txt` if desired.

| Download | Target |
| --- | --- |
| `windows-x64.zip` | Windows 10/11 x64 |
| `linux-x64.tar.gz` | Linux x64 with glibc 2.35+ and desktop libraries |
| `macos-arm64.zip` | Apple Silicon, macOS 14+ |
| `macos-x64.zip` | Intel Mac, macOS 15+ |

The builds are not signed with a publisher certificate; macOS apps are ad-hoc signed for local execution and are not notarized. Packaged builds use regular minimize. Optional tray integration is available when running from source on Windows/Linux. Session totals are temporary and can include duplicate VPN traffic when all adapters are selected.

The release pipeline runs unit/desktop checks and starts each packaged app before publishing. This does not replace manual testing on every desktop environment.
