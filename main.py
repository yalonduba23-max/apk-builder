import os
import re
import socket
import ssl
import requests
import traceback
import time
from threading import Thread

# Kivy UI Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

# --- CRASH PREVENTION: SSL CERTIFICATE FIX ---
# On Android, Python cannot find the SSL store. We force it here.
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['SSL_CERT_DIR'] = os.path.dirname(certifi.where())
except ImportError:
    pass

class ConsoleUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Set Black Background
        with self.canvas.before:
            Color(0, 0, 0, 1) # Absolute Black
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Scrollable Label for "Console" output
        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=10)
        
        self.log_label = Label(
            text="[b][SYSTEM][/b] Booting Console...\n[~] Safe Environment Loaded.",
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(0, 1, 0, 1), # Terminal Green
            font_size='13sp',
            font_name='Roboto' # Default Kivy font
        )
        
        self.log_label.bind(size=self._update_text_size)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width * 0.98, None)
        instance.height = max(instance.texture_size[1], self.scroll.height)

    # --- THREAD-SAFE LOGGING FUNCTION ---
    # color options: 00FF00 (Green), FF0000 (Red), 00FFFF (Cyan), FFFF00 (Yellow)
    def log(self, message, color="00FF00"):
        def _append_text(dt):
            timestamp = time.strftime("%H:%M:%S")
            self.log_label.text += f"\n[[{color}] {timestamp} [/{color}]] {message}"
            # Auto-scroll to bottom
            self.scroll.scroll_y = 0
        Clock.schedule_once(_append_text)

class BugHunterApp(App):
    def build(self):
        self.ui = ConsoleUI()
        return self.ui

    def on_start(self):
        # Run logic in background thread to prevent "App Not Responding" (ANR)
        Thread(target=self.safe_run, daemon=True).start()

    def safe_run(self):
        """Wrapper to catch every single possible error and print to screen"""
        try:
            self.run_logic()
        except Exception:
            # If the app crashes, it captures the error and displays it in RED
            error_details = traceback.format_exc()
            self.ui.log("\n" + "!"*40, "FF0000")
            self.ui.log("CRITICAL ERROR ENCOUNTERED", "FF0000")
            self.ui.log(error_details, "FF0000")
            self.ui.log("!"*40 + "\n", "FF0000")

    def run_logic(self):
        """The actual Bug Hunting code"""
        self.ui.log("Starting Phase 1: Network Check...", "00FFFF")
        
        # 1. Check Local IP (Android 13+ safe method)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.ui.log(f"[+] Local IP detected: {local_ip}")
        except Exception as e:
            self.ui.log(f"[!] IP Check failed: {e}", "FFFF00")
            return

        # 2. Portal Detection
        self.ui.log("Phase 2: Detecting Portal...", "00FFFF")
        domain = None
        try:
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=7, allow_redirects=False)
            if 'Location' in r.headers:
                domain = r.headers['Location'].split('/')[2].split(':')[0]
                self.ui.log(f"[+] Target Portal Found: {domain}")
            else:
                self.ui.log("[!] No Redirect found. Portal might be open or blocked.", "FFFF00")
        except Exception as e:
            self.ui.log(f"[!] Network Timeout/Error: {e}", "FF0000")

        if not domain:
            self.ui.log("[*] Scanner stopped: No domain to audit.", "FFFF00")
            return

        # 3. Extraction (Scraping the Portal page)
        self.ui.log(f"Phase 3: Scraping {domain}...", "00FFFF")
        try:
            res = requests.get(f"http://{domain}", timeout=10)
            regex = r'(?i)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+(com|net|org|io|me|be)'
            found = set(re.findall(regex, res.text))
            self.ui.log(f"[+] Found {len(found)} candidate hosts.")
            # Resolve and test logic would go here
        except Exception as e:
            self.ui.log(f"[!] Scrape error: {e}", "FF0000")

        self.ui.log("--- SCAN COMPLETE ---", "00FFFF")

if __name__ == "__main__":
    BugHunterApp().run()
