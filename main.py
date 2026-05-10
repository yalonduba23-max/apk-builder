from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
import threading
import socket
import ssl
import re
import requests
from urllib.parse import urljoin, urlparse

class BugHunterApp(MDApp):
    def build(self):
        self.scanning = False 
        self.nav_layout = MDNavigationLayout()
        self.outer_sm = ScreenManager()
        self.main_screen_wrapper = Screen(name="main_wrapper")
        self.main_container = MDBoxLayout(orientation='horizontal')

        # --- LEFT RAIL ---
        self.left_rail = MDBoxLayout(orientation='vertical', size_hint_x=None, width=dp(50), md_bg_color=(0, 0, 0, 1), padding=[0, dp(10), 0, 0])
        self.menu_btn = MDIconButton(icon="menu", theme_text_color="Custom", text_color=(1, 1, 1, 1), on_release=lambda x: self.nav_drawer.set_state("open"))
        self.left_rail.add_widget(self.menu_btn)
        self.left_rail.add_widget(Widget())

        # --- RIGHT CONTENT ---
        self.right_content = MDBoxLayout(orientation='vertical')
        self.top_bar = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), md_bg_color=(0, 1, 0, 1))
        
        self.vpn_btn = MDFlatButton(text="VPN", theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("vpn"))
        self.logs_btn = MDFlatButton(text="LOGS", theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("logs"))
        self.gear_btn = MDIconButton(icon="cog", theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("settings"))

        self.top_bar.add_widget(self.vpn_btn)
        self.top_bar.add_widget(self.logs_btn)
        self.top_bar.add_widget(Widget())
        self.top_bar.add_widget(self.gear_btn)

        # --- SCREENS ---
        self.sm = ScreenManager()
        
        # VPN SCREEN
        self.vpn_screen = Screen(name="vpn")
        vpn_layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.status_label = MDLabel(text="Status: Idle", halign="center", font_style="H6")
        self.scan_btn = MDRaisedButton(text="START SCAN", pos_hint={"center_x": .5}, md_bg_color=(0, 0.5, 1, 1), on_release=self.toggle_scan)
        vpn_layout.add_widget(self.status_label)
        vpn_layout.add_widget(self.scan_btn)
        self.vpn_screen.add_widget(vpn_layout)

        # LOGS SCREEN
        self.logs_screen = Screen(name="logs")
        self.log_scroll = MDScrollView()
        self.log_text = MDLabel(text="--- System Logs ---\n", size_hint_y=None, halign="left", theme_text_color="Secondary", padding=[dp(10), dp(10)])
        self.log_text.bind(texture_size=self.log_text.setter('size'))
        self.log_scroll.add_widget(self.log_text)
        self.logs_screen.add_widget(self.log_scroll)

        self.sm.add_widget(self.vpn_screen)
        self.sm.add_widget(self.logs_screen)
        self.sm.add_widget(Screen(name="settings"))

        self.right_content.add_widget(self.top_bar)
        self.right_content.add_widget(self.sm)
        self.main_container.add_widget(self.left_rail)
        self.main_container.add_widget(self.right_content)
        self.main_screen_wrapper.add_widget(self.main_container)
        self.outer_sm.add_widget(self.main_screen_wrapper)
        self.nav_layout.add_widget(self.outer_sm)

        # SIDE MENU
        self.nav_drawer = MDNavigationDrawer(radius=(0, dp(16), dp(16), 0), width=dp(120))
        self.nav_layout.add_widget(self.nav_drawer)

        return self.nav_layout

    def add_log(self, message):
        def update_label(dt):
            self.log_text.text += f"[*] {message}\n"
        Clock.schedule_once(update_label)

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

    def toggle_scan(self, instance):
        if not self.scanning:
            self.scanning = True
            self.scan_btn.text = "STOP SCAN"
            self.scan_btn.md_bg_color = (1, 0, 0, 1)
            self.status_label.text = "Status: Scanning..."
            self.add_log("Scan Started...")
            threading.Thread(target=self.run_scanner, daemon=True).start()
        else:
            self.scanning = False
            self.add_log("Stopping scan...")

    def run_scanner(self):
        # CONFIG FROM SUCCESSFUL HUNT.PY
        BASH_REGEX = r'(?i)((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|me|be))'
        EXCLUDE_FILTER = r'\.(jpg|jpeg|png|gif|ico|svg|css|js|mp4|woff|woff2|ttf)$'

        try:
            # Phase 1: Portal Detection
            if not self.scanning: return
            self.add_log("Detecting Captive Portal...")
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5, allow_redirects=False)
            portal_url = r.headers.get('Location')
            
            if not portal_url:
                self.add_log("No Portal found. Check connection.")
                Clock.schedule_once(lambda dt: self.finish_scan("No Portal Found"))
                return
            
            domain = urlparse(portal_url).netloc
            self.add_log(f"Portal: {domain}")

            # Phase 2: Mirroring (HTML + JS)
            if not self.scanning: return
            self.add_log("Mirroring site (Downloading JS)...")
            main_res = requests.get(portal_url, timeout=10)
            combined_content = main_res.text
            
            # Find JS files
            js_paths = re.findall(r'src=["\'](.*\.js.*?)["\']', main_res.text)
            for path in js_paths:
                if not self.scanning: return
                js_url = urljoin(portal_url, path)
                try:
                    self.add_log(f"Fetching JS: {path.split('/')[-1]}")
                    combined_content += "\n" + requests.get(js_url, timeout=5).text
                except: pass

            # Extraction
            if not self.scanning: return
            raw_matches = re.findall(BASH_REGEX, combined_content)
            
            final_domains = set()
            for m in raw_matches:
                if not re.search(EXCLUDE_FILTER, m, re.IGNORECASE):
                    final_domains.add(m.lower())
            
            self.add_log(f"Extracted {len(final_domains)} unique domains.")

            # Phase 3: Handshake
            unique_ips = set()
            for d in final_domains:
                if not self.scanning: return
                try:
                    ip = socket.gethostbyname(d)
                    unique_ips.add(ip)
                except: continue

            self.add_log(f"Testing {len(unique_ips)} unique IPs...")
            working_ips = []
            for ip in sorted(unique_ips):
                if not self.scanning: break
                ok, msg = self.check_handshake(ip)
                if ok:
                    self.add_log(f"FOUND: {ip} (101 OK)")
                    working_ips.append(ip)
                else:
                    self.add_log(f"FAIL: {ip} ({msg[:15]})")

            result_msg = f"Done. Found {len(working_ips)} Bugs." if self.scanning else "Aborted."
            self.add_log(result_msg)
            Clock.schedule_once(lambda dt: self.finish_scan(result_msg))

        except Exception as e:
            self.add_log(f"Error: {e}")
            Clock.schedule_once(lambda dt: self.finish_scan("Scan Error"))

    def check_handshake(self, ip):
        my_server = "web.chomba.tech"
        ws_path = "/vless"
        header = (
            f"GET {ws_path} HTTP/1.1\r\n"
            f"Host: {my_server}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            context = ssl.create_default_context()
            ssock = context.wrap_socket(sock, server_hostname=my_server)
            ssock.connect((ip, 443))
            ssock.send(header.encode())
            res = ssock.recv(1024).decode(errors='ignore')
            ssock.close()
            return ("101" in res, res.splitlines()[0] if res else "No Response")
        except Exception as e:
            return (False, str(e))

    def finish_scan(self, msg):
        self.scanning = False
        self.status_label.text = f"Status: {msg}"
        self.scan_btn.text = "START SCAN"
        self.scan_btn.md_bg_color = (0, 0.5, 1, 1)

if __name__ == "__main__":
    BugHunterApp().run()
