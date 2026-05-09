import os, re, socket, ssl, requests, traceback, time, threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import platform

# --- ANDROID SSL FIX ---
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except:
    pass

KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "BOMBO-CLAT BUG HUNTER"
        elevation: 4
        md_bg_color: 0, 0, 0, 1
        specific_text_color: 0, 0.7, 1, 1

    MDTabs:
        id: tabs
        on_tab_switch: app.on_tab_switch(*args)
        background_color: 0, 0, 0, 1
        indicator_color: 0, 0.7, 1, 1
        text_color_normal: 0.5, 0.5, 0.5, 1
        text_color_active: 0, 0.7, 1, 1

<DashboardTab>:
    title: "Dashboard"
    MDFloatLayout:
        md_bg_color: 0, 0, 0, 1

        MDLabel:
            text: "YOUR DEVICE IP"
            halign: "center"
            pos_hint: {"center_y": .85}
            theme_text_color: "Custom"
            text_color: 0, 0.7, 1, 1
            font_style: "Caption"

        MDLabel:
            id: ip_display
            text: app.local_ip
            halign: "center"
            pos_hint: {"center_y": .80}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H4"

        # Progress Ring
        canvas.after:
            Color:
                rgba: (0, 0.7, 1, 0.2)
            Line:
                circle: (self.center_x, self.center_y - dp(20), dp(80))
                width: dp(4)
            Color:
                rgba: (0, 0.7, 1, 1)
            Line:
                circle: (self.center_x, self.center_y - dp(20), dp(80), 0, app.progress_angle)
                width: dp(5)
                cap: 'round'

        MDFloatingActionButton:
            icon: "play" if not app.scanning else "stop"
            icon_size: "64sp"
            md_bg_color: 0, 0.7, 1, 1
            pos_hint: {"center_x": .5, "center_y": .47}
            on_release: app.toggle_scan()

        MDLabel:
            text: app.status_text
            halign: "center"
            pos_hint: {"center_y": .2}
            theme_text_color: "Secondary"

<LogsTab>:
    title: "Logs"
    MDBoxLayout:
        padding: "10dp"
        md_bg_color: 0, 0, 0, 1
        ScrollView:
            id: scroll
            MDLabel:
                id: log_output
                text: app.log_text
                markup: True
                size_hint_y: None
                height: self.texture_size[1]
                halign: "left"
                valign: "top"
                theme_text_color: "Custom"
                text_color: 0, 1, 0, 1
                font_style: "Caption"
                font_name: "Roboto"
'''

class DashboardTab(MDFloatLayout, MDTabsBase):
    pass

class LogsTab(MDFloatLayout, MDTabsBase):
    pass

class BugHunterApp(MDApp):
    # Reactive Properties
    local_ip = StringProperty("Detecting...")
    status_text = StringProperty("Press Start to Begin Scan")
    log_text = StringProperty("[color=00FF00][SYSTEM][/color] Booting...\\n")
    progress_angle = NumericProperty(0)
    scanning = threading.Event()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        # Initial Tab Setup
        self.root.ids.tabs.add_widget(DashboardTab())
        self.root.ids.tabs.add_widget(LogsTab())
        # Initial IP Detection
        Clock.schedule_once(lambda dt: self.get_initial_ip(), 0.5)

    def get_initial_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
            s.close()
            self.write_log(f"Ready. Device connected at {self.local_ip}")
        except:
            self.local_ip = "Offline"
            self.write_log("No active network connection detected.", "FF0000")

    def write_log(self, msg, color="00FF00"):
        def _update(dt):
            ts = time.strftime("%H:%M:%S")
            self.log_text += f"\\n[[color={color}]{ts}[/color]] {msg}"
        Clock.schedule_once(_update)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        pass

    def toggle_scan(self):
        if not self.scanning.is_set():
            self.scanning.set()
            self.status_text = "Scanning..."
            threading.Thread(target=self.run_full_scan, daemon=True).start()
        else:
            self.scanning.clear()
            self.status_text = "Scan Aborted"
            self.progress_angle = 0

    def run_full_scan(self):
        try:
            # Phase 1: Portal Detect
            self.update_progress(10)
            self.write_log("Phase 1: Detecting Portal...", "00FFFF")
            target = self.detect_portal()
            
            if not target or not self.scanning.is_set():
                self.write_log("Failed to locate portal.", "FF0000")
                self.scanning.clear()
                return

            self.update_progress(30)
            self.write_log(f"Phase 2: Scraping memory from {target}...", "00FFFF")
            
            # Phase 2: Scrape site (In-Memory)
            r = requests.get(f"http://{target}", timeout=10)
            regex = r'(?i)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+(com|net|org|io|me|be)'
            found_raw = re.finditer(regex, r.text)
            
            unique_domains = set()
            exclude = ('.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.css', '.js', '.mp4')
            for m in found_raw:
                d = m.group(0).lower()
                if not d.endswith(exclude):
                    unique_domains.add(d)

            self.write_log(f"Found {len(unique_domains)} domains in memory storage.")
            self.update_progress(50)

            # Phase 3: Resolution & TLS Handshake
            self.write_log(f"Phase 3: Testing VLESS (SNI: web.chomba.tech)...", "00FFFF")
            ips = set()
            for d in unique_domains:
                if not self.scanning.is_set(): break
                try: ips.add(socket.gethostbyname(d))
                except: continue
            
            self.write_log(f"Resolving complete. Testing {len(ips)} IPs.")
            
            found_bugs = []
            count = 0
            for ip in ips:
                if not self.scanning.is_set(): break
                count += 1
                self.update_progress(50 + (count/len(ips) * 50))
                
                self.write_log(f"Testing Handshake -> {ip}")
                if self.test_vless(ip):
                    self.write_log(f"SUCCESS: {ip} CONNECTED (101 OK)", "FFFF00")
                    found_bugs.append(ip)
                
            self.write_log(f"--- SCAN FINISHED. Found {len(found_bugs)} hosts ---", "00FFFF")
            self.status_text = f"Finished. Found {len(found_bugs)} Bugs."
            self.scanning.clear()

        except Exception as e:
            self.write_log(f"Fatal Crash: {str(e)}", "FF0000")
            self.write_log(traceback.format_exc(), "FF0000")
            self.scanning.clear()

    def update_progress(self, percent):
        self.progress_angle = (percent / 100) * 360

    def detect_portal(self):
        try:
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5, allow_redirects=False)
            if 'Location' in r.headers:
                return r.headers['Location'].split('/')[2].split(':')[0]
            # Fallback to gateway logic
            subnet = ".".join(self.local_ip.split('.')[:-1])
            for gw in [f"{subnet}.1", f"{subnet}.254"]:
                try:
                    if requests.get(f"http://{gw}", timeout=2).status_code in [200, 302]: return gw
                except: continue
        except: pass
        return None

    def test_vless(self, ip):
        header = (
            f"GET /vless HTTP/1.1\\r\\nHost: web.chomba.tech\\r\\n"
            f"Upgrade: websocket\\r\\nConnection: Upgrade\\r\\n"
            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\\r\\n"
            f"Sec-WebSocket-Version: 13\\r\\n\\r\n"
        )
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ssock = ctx.wrap_socket(sock, server_hostname="web.chomba.tech")
            ssock.connect((ip, 443))
            ssock.send(header.encode())
            res = ssock.recv(1024).decode(errors='ignore')
            ssock.close()
            return "101" in res
        except: return False

if __name__ == "__main__":
    BugHunterApp().run()
