import tkinter as tk
from tkinter import messagebox
import psutil
import time
import socket
import subprocess
import os
import sys
import threading
import winreg
import ctypes

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    messagebox.showerror("Missing Libraries", "Please run: pip install pystray pillow")
    sys.exit(1)

class LiteNetworkMonitor:
    def __init__(self, root):
        self.root = root
        self.root.geometry("200x110")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        # App State & Settings
        self.paused = False
        self.use_bits = False
        self.selected_nic = "All"
        self.themes = [
            {"name": "Dark Hacker", "bg": "#1e1e1e", "fg": "#00ffcc", "font": ("Consolas", 10, "bold")},
            {"name": "Light Mode", "bg": "#f3f3f3", "fg": "#333333", "font": ("Segoe UI", 10, "bold")},
            {"name": "Matrix", "bg": "#000000", "fg": "#00ff00", "font": ("Courier", 10, "bold")}
        ]
        self.current_theme_idx = 0
        
        # Baselines
        self.reset_baselines()
        
        # Window Dragging Variables
        self.click_x = 0
        self.click_y = 0
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.move_window)
        self.root.bind('<Double-Button-1>', self.copy_speed)

        # UI Initialization
        self.lbl_download = tk.Label(root)
        self.lbl_download.pack(pady=(15, 0))
        self.lbl_upload = tk.Label(root)
        self.lbl_upload.pack(pady=(2, 5))
        self.lbl_session = tk.Label(root)
        self.lbl_session.pack()
        self.lbl_boot = tk.Label(root)
        self.lbl_boot.pack()

        # Top Right Controls (X, Minimize, Dropdown)
        self.btn_close = tk.Label(root, text="X", cursor="hand2")
        self.btn_close.place(x=180, y=5)
        self.btn_close.bind("<Button-1>", lambda e: self.exit_app())

        self.btn_min = tk.Label(root, text="—", cursor="hand2")
        self.btn_min.place(x=160, y=5)
        self.btn_min.bind("<Button-1>", lambda e: self.minimize_to_tray())

        self.btn_menu = tk.Label(root, text="▼", cursor="hand2", font=("Segoe UI", 8))
        self.btn_menu.place(x=140, y=7)
        self.btn_menu.bind("<Button-1>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))

        self.apply_theme()
        self.build_context_menu()
        
        # Apply 4px Border Radius (Native Windows API)
        self.root.update_idletasks()
        self.apply_rounded_corners()

        self.update_stats()

    def apply_rounded_corners(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()
            # 8px diameter = 4px radius
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, 200, 110, 8, 8)
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass # Failsafe if OS blocks region modification

    def reset_baselines(self):
        stats = self.get_net_stats()
        self.last_recv = stats.bytes_recv
        self.last_sent = stats.bytes_sent
        self.start_recv = self.last_recv
        self.start_sent = self.last_sent
        self.last_time = time.time()

    def get_net_stats(self):
        if self.selected_nic == "All":
            return psutil.net_io_counters()
        else:
            return psutil.net_io_counters(pernic=True).get(self.selected_nic, psutil.net_io_counters())

    def apply_theme(self):
        theme = self.themes[self.current_theme_idx]
        self.root.configure(bg=theme["bg"])
        
        # Update control buttons
        for btn in (self.btn_close, self.btn_min):
            btn.config(bg=theme["bg"], fg="#888888", font=theme["font"])
        self.btn_menu.config(bg=theme["bg"], fg="#888888")
        
        small_font = (theme["font"][0], 8)
        self.lbl_download.config(bg=theme["bg"], fg=theme["fg"], font=theme["font"])
        self.lbl_upload.config(bg=theme["bg"], fg=theme["fg"], font=theme["font"])
        self.lbl_session.config(bg=theme["bg"], fg="#888888", font=small_font)
        self.lbl_boot.config(bg=theme["bg"], fg="#888888", font=small_font)

    # --- Context Menu ---
    def build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.root.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))
        
        self.menu.add_command(label="Minimize to Tray", command=self.minimize_to_tray)
        self.menu.add_separator()
        
        self.menu.add_command(label="Restart Session", command=self.reset_baselines)
        self.menu.add_command(label="Pause / Resume", command=self.toggle_pause)
        self.menu.add_command(label="Toggle Theme", command=self.cycle_theme)
        self.menu.add_command(label="Toggle Bits/Bytes", command=self.toggle_units)
        
        self.nic_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Select Network Card", menu=self.nic_menu)
        self.refresh_nic_menu()

        self.menu.add_separator()
        
        # Dynamic Auto-Start Checkbox
        self.autostart_var = tk.BooleanVar(value=self.check_autostart_status())
        self.menu.add_checkbutton(label="Auto-Start with Windows", variable=self.autostart_var, command=self.toggle_autostart)
        
        self.menu.add_command(label="Check Latency (Ping)", command=self.check_latency)
        self.menu.add_command(label="Show IP Info", command=self.show_ip)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.exit_app)

    def refresh_nic_menu(self):
        self.nic_menu.delete(0, 'end')
        self.nic_menu.add_command(label="All (Default)", command=lambda: self.set_nic("All"))
        for nic in psutil.net_io_counters(pernic=True).keys():
            self.nic_menu.add_command(label=nic, command=lambda n=nic: self.set_nic(n))

    def set_nic(self, nic_name):
        self.selected_nic = nic_name
        self.reset_baselines()

    # --- Core Features ---
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.lbl_download.config(text="[ PAUSED ]")
            self.lbl_upload.config(text="Double-click to copy")

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.themes)
        self.apply_theme()

    def toggle_units(self):
        self.use_bits = not self.use_bits

    def show_ip(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        messagebox.showinfo("Network Info", f"Hostname: {hostname}\nLocal IP: {ip}\nAdapter: {self.selected_nic}")

    def check_latency(self):
        # Runs in a separate thread to prevent UI freezing
        threading.Thread(target=self._run_ping, daemon=True).start()

    def _run_ping(self):
        try:
            output = subprocess.check_output("ping -n 1 -w 1000 8.8.8.8", shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if "time=" in output:
                ms = output.split("time=")[1].split("ms")[0].strip()
                messagebox.showinfo("Latency Check", f"Current Latency: {ms} ms")
            else:
                messagebox.showerror("Latency Check", "Could not reach server. Check internet.")
        except Exception:
            messagebox.showerror("Latency Check", "Ping failed.")

    def copy_speed(self, event=None):
        if not self.paused:
            text_to_copy = f"{self.lbl_download.cget('text')} | {self.lbl_upload.cget('text')}"
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            
            original_color = self.lbl_download.cget("fg")
            self.lbl_download.config(fg="#ffffff")
            self.root.after(200, lambda: self.lbl_download.config(fg=original_color))

    def check_autostart_status(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "LiteNetMonitor")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    def toggle_autostart(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "LiteNetMonitor"
        exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if not self.autostart_var.get():
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            else:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", f"Could not modify registry: {e}")
            self.autostart_var.set(not self.autostart_var.get()) # Revert toggle on fail

    # --- System Tray & Dragging ---
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(43, 43, 43))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(0, 255, 204))
        return image

    def minimize_to_tray(self):
        self.root.withdraw()
        menu = pystray.Menu(
            pystray.MenuItem('Show', self.restore_from_tray, default=True),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("LiteNetMon", self.create_tray_icon(), "Lite NetMonitor", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.root.after(0, self.root.deiconify)

    def exit_app(self, icon=None, item=None):
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.root.destroy()
        sys.exit()

    def start_move(self, event):
        self.click_x = event.x
        self.click_y = event.y

    def move_window(self, event):
        x = self.root.winfo_x() - self.click_x + event.x
        y = self.root.winfo_y() - self.click_y + event.y
        self.root.geometry(f"+{x}+{y}")

    # --- Update Loop ---
    def update_stats(self):
        if not self.paused:
            stats = self.get_net_stats()
            current_time = time.time()
            time_elapsed = current_time - self.last_time

            down_speed = (stats.bytes_recv - self.last_recv) / time_elapsed
            up_speed = (stats.bytes_sent - self.last_sent) / time_elapsed

            self.lbl_download.config(text=f"DL: {self.format_speed(down_speed)}")
            self.lbl_upload.config(text=f"UL: {self.format_speed(up_speed)}")

            session_total = (stats.bytes_recv - self.start_recv) + (stats.bytes_sent - self.start_sent)
            boot_total = stats.bytes_recv + stats.bytes_sent
            
            self.lbl_session.config(text=f"Session: {session_total / (1024*1024):.1f} MB")
            self.lbl_boot.config(text=f"Since Boot: {boot_total / (1024*1024):.1f} MB")

            self.last_recv = stats.bytes_recv
            self.last_sent = stats.bytes_sent
            self.last_time = current_time

        self.root.after(1000, self.update_stats)

    def format_speed(self, bytes_per_sec):
        multiplier = 8 if self.use_bits else 1
        unit = "b" if self.use_bits else "B"
        val = bytes_per_sec * multiplier

        if val < 1024 * 1024:
            return f"{val / 1024:.2f} K{unit}/s"
        else:
            return f"{val / (1024 * 1024):.2f} M{unit}/s"

if __name__ == "__main__":
    root = tk.Tk()
    app = LiteNetworkMonitor(root)
    root.mainloop()