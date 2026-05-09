import os
import sys
import traceback
import socket
import requests

LOG_FILE = '/sdcard/bughunter_crash.txt'
def log_exception(exc_type, exc_value, exc_tb):
    with open(LOG_FILE, 'w') as f:
        f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
sys.excepthook = log_exception

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from threading import Thread


class BugHunterCore:
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    def detect_portal(self, ip):
        try:
            r = requests.get("http://clients3.google.com/generate_204",
                           timeout=5, allow_redirects=True)
            if r.status_code == 204:
                return None
            return r.url
        except:
            return None

    def extract_domains(self, portal_url):
        if not portal_url:
            return []
        try:
            from urllib.parse import urlparse
            parsed = urlparse(portal_url)
            return [parsed.netloc] if parsed.netloc else []
        except:
            return []

    def check_vless(self, target):
        try:
            r = requests.get(f"http://{target}", timeout=3)
            return r.status_code == 200
        except:
            return False


class HunterUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.core = BugHunterCore()

        self.btn = Button(text="START BUG HUNT", size_hint_y=0.1)
        self.btn.bind(on_press=self.start_hunt)

        self.log_area = Label(
            text="Ready...",
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.log_area.bind(size=self.log_area.setter('text_size'))
        self.log_area.bind(texture_size=self.log_area.setter('size'))

        self.scroll = ScrollView()
        self.scroll.add_widget(self.log_area)

        self.add_widget(self.btn)
        self.add_widget(self.scroll)

    def log(self, text):
        self.log_area.text += f"\n{text}"

    def start_hunt(self, instance):
        self.log_area.text = "[*] Starting..."
        Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        ip = self.core.get_local_ip()
        if not ip:
            self.log("[!] No WiFi detected")
            return

        self.log(f"[*] Local IP: {ip}")

        portal = self.core.detect_portal(ip)
        if not portal:
            self.log("[!] No captive portal detected")
            return
        self.log(f"[+] Portal: {portal}")

        domains = self.core.extract_domains(portal)
        self.log(f"[*] Found {len(domains)} domains. Resolving...")

        ips = set()
        for d in domains:
            try:
                ips.add(socket.gethostbyname(d))
            except:
                continue

        if not ips:
            self.log("[!] No IPs resolved")
            return

        for target in ips:
            self.log(f"[~] Testing {target}...")
            if self.core.check_vless(target):
                self.log(f"    [✔] WORKING: {target}")
            else:
                self.log(f"    [✗] No response: {target}")


class BugHunterApp(App):
    def build(self):
        return HunterUI()


if __name__ == "__main__":
    BugHunterApp().run()
