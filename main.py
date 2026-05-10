import asyncio, struct, uuid, aiohttp, ssl, socket, re, threading, requests, os
from urllib.parse import urljoin, urlparse
from kivy.utils import platform
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.clipboard import Clipboard

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField

# ================= HARDCODED VPN CONFIG =================
USER_UUID       = "4224f578-6c71-4cf2-ae77-3cf1d8878fed"
ACTUAL_SERVER   = "web.chomba.tech"
WS_PATH         = "/vless"
CONNECT_IP      = "104.26.3.143" 
PORT            = 443
# ========================================================

class BugHunterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        
        self.scanning = False
        self.connected = False
        self.selected_bug = ACTUAL_SERVER
        
        self.nav_layout = MDNavigationLayout()
        self.outer_sm = ScreenManager()
        self.main_screen_wrapper = Screen(name="main_wrapper")
        self.main_container = MDBoxLayout(orientation='horizontal')

        # --- LEFT RAIL (Fixed UI) ---
        self.left_rail = MDBoxLayout(orientation='vertical', size_hint_x=None, width=dp(50), md_bg_color=(0, 0, 0, 1), padding=[0, dp(10), 0, 0])
        self.menu_btn = MDIconButton(icon="menu", theme_text_color="Custom", text_color=(1, 1, 1, 1), on_release=lambda x: self.nav_drawer.set_state("open"))
        self.left_rail.add_widget(self.menu_btn)
        self.left_rail.add_widget(Widget())

        # --- RIGHT CONTENT ---
        self.right_content = MDBoxLayout(orientation='vertical')
        self.top_bar = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), md_bg_color=(0.1, 0.1, 0.1, 1))
        
        self.vpn_btn = MDFlatButton(text="VPN", theme_text_color="Custom", text_color=(1,1,1,1), on_release=lambda x: self.switch_screen("vpn"))
        self.logs_btn = MDFlatButton(text="LOGS", theme_text_color="Custom", text_color=(1,1,1,1), on_release=lambda x: self.switch_screen("logs"))
        self.copy_btn = MDIconButton(icon="content-copy", theme_text_color="Custom", text_color=(0,1,0,1), on_release=self.copy_logs)

        self.top_bar.add_widget(self.vpn_btn)
        self.top_bar.add_widget(self.logs_btn)
        self.top_bar.add_widget(Widget())
        self.top_bar.add_widget(self.copy_btn)

        # SCREENS
        self.sm = ScreenManager()
        
        # VPN SCREEN
        self.vpn_screen = Screen(name="vpn")
        vpn_layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.status_label = MDLabel(text="DISCONNECTED", halign="center", font_style="H4", theme_text_color="Error")
        self.bug_info = MDLabel(text=f"Bug: {self.selected_bug}", halign="center", font_style="Caption", theme_text_color="Secondary")
        self.connect_btn = MDRaisedButton(text="CONNECT", size_hint=(.8, None), pos_hint={"center_x": .5}, md_bg_color=(0, .6, 0, 1), on_release=self.toggle_vpn)
        self.scan_btn = MDRaisedButton(text="START SCAN", size_hint=(.8, None), pos_hint={"center_x": .5}, on_release=self.toggle_scan)
        vpn_layout.add_widget(Widget()); vpn_layout.add_widget(self.status_label); vpn_layout.add_widget(self.bug_info)
        vpn_layout.add_widget(self.connect_btn); vpn_layout.add_widget(self.scan_btn); vpn_layout.add_widget(Widget())
        self.vpn_screen.add_widget(vpn_layout)

        # LOGS SCREEN (Thorough Debugging)
        self.logs_screen = Screen(name="logs")
        self.log_scroll = MDScrollView()
        self.log_text = MDLabel(text="--- System Ready ---\n", size_hint_y=None, halign="left", font_style="Caption", theme_text_color="Secondary", padding=[dp(10), dp(10)])
        self.log_text.bind(texture_size=self.log_text.setter('size'))
        self.log_scroll.add_widget(self.log_text)
        self.logs_screen.add_widget(self.log_scroll)

        self.sm.add_widget(self.vpn_screen); self.sm.add_widget(self.logs_screen)
        self.right_content.add_widget(self.top_bar); self.right_content.add_widget(self.sm)
        self.main_container.add_widget(self.left_rail); self.main_container.add_widget(self.right_content)
        self.main_screen_wrapper.add_widget(self.main_container); self.outer_sm.add_widget(self.main_screen_wrapper)
        self.nav_layout.add_widget(self.outer_sm)

        # DRAWER (Setup Bug Host)
        self.nav_drawer = MDNavigationDrawer(radius=(0, dp(16), dp(16), 0))
        drawer_box = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.bug_input = MDTextField(hint_text="Bug Host", text=ACTUAL_SERVER)
        drawer_box.add_widget(MDLabel(text="Server Settings", font_style="H6"))
        drawer_box.add_widget(self.bug_input)
        drawer_box.add_widget(MDRaisedButton(text="APPLY BUG", on_release=self.apply_bug))
        drawer_box.add_widget(Widget())
        self.nav_drawer.add_widget(drawer_box); self.nav_layout.add_widget(self.nav_drawer)

        return self.nav_layout

    def add_log(self, message):
        def update_label(dt): self.log_text.text += f"[*] {message}\n"
        Clock.schedule_once(update_label)

    def copy_logs(self, instance):
        Clipboard.copy(self.log_text.text)
        self.add_log("Logs copied.")

    def switch_screen(self, screen_name): self.sm.current = screen_name

    def apply_bug(self, instance):
        self.selected_bug = self.bug_input.text
        self.bug_info.text = f"Bug: {self.selected_bug}"
        self.add_log(f"Manual SNI updated: {self.selected_bug}")
        self.nav_drawer.set_state("close")

    # ================= SCANNER (Exact Logic Provided) =================
    def toggle_scan(self, instance):
        if not self.scanning:
            self.scanning, self.scan_btn.text = True, "STOP SCAN"
            self.status_label.text = "SCANNING..."
            threading.Thread(target=self.run_scanner, daemon=True).start()
        else: self.scanning = False

    def run_scanner(self):
        BASH_REGEX = r'(?i)((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|me|be))'
        EXCLUDE_FILTER = r'\.(jpg|jpeg|png|gif|ico|svg|css|js|mp4|woff|woff2|ttf)$'
        try:
            self.add_log("Phase 1: Portal Detection...")
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5, allow_redirects=False)
            portal = r.headers.get('Location')
            if not portal:
                self.add_log("No Portal Found.")
                return
            
            self.add_log(f"Phase 2: Mirroring {urlparse(portal).netloc}")
            res = requests.get(portal, timeout=10)
            content = res.text
            js_paths = re.findall(r'src=["\'](.*\.js.*?)["\']', content)
            for p in js_paths:
                if not self.scanning: break
                try: 
                    self.add_log(f"Downloading JS: {p.split('/')[-1]}")
                    content += "\n" + requests.get(urljoin(portal, p), timeout=5).text
                except: pass

            matches = list(set(re.findall(BASH_REGEX, content)))
            for m in matches:
                if not self.scanning: break
                if not re.search(EXCLUDE_FILTER, m, re.IGNORECASE):
                    self.add_log(f"Handshake Test: {m}")
                    if self.handshake_verify(m):
                        self.selected_bug = m
                        self.add_log(f"BUG FOUND: {m} (101 OK)")
                        break
        except Exception as e: self.add_log(f"Scanner Error: {e}")
        finally:
            self.scanning = False
            Clock.schedule_once(lambda dt: self.finish_scan())

    def handshake_verify(self, bug):
        h = f"GET {WS_PATH} HTTP/1.1\r\nHost: {ACTUAL_SERVER}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n"
        try:
            s = socket.create_connection((bug, 443), timeout=3)
            ss = ssl._create_unverified_context().wrap_socket(s, server_hostname=ACTUAL_SERVER)
            ss.send(h.encode()); res = ss.recv(1024).decode(errors='ignore'); ss.close()
            return "101" in res
        except: return False

    def finish_scan(self):
        self.scan_btn.text, self.status_label.text = "START SCAN", "READY"
        self.bug_info.text = f"Bug: {self.selected_bug}"

    # ================= VPN ENGINE (VLESS over WSS) =================
    def toggle_vpn(self, instance):
        if not self.connected:
            self.connected = True
            self.connect_btn.text, self.connect_btn.md_bg_color = "STOP", (1, 0, 0, 1)
            self.status_label.text, self.status_label.theme_text_color = "CONNECTING...", "Primary"
            if platform == 'android': self.android_service("START")
            threading.Thread(target=self.run_engine, daemon=True).start()
        else:
            self.connected = False
            self.connect_btn.text, self.connect_btn.md_bg_color = "CONNECT", (0, .6, 0, 1)
            self.status_label.text, self.status_label.theme_text_color = "DISCONNECTED", "Error"
            if platform == 'android': self.android_service("STOP")

    def android_service(self, action):
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            VpnService = autoclass('android.net.VpnService')
            Intent = autoclass('android.content.Intent')
            if action == "START":
                p = VpnService.prepare(activity)
                if p: activity.startActivityForResult(p, 0)
                activity.startService(Intent(activity, autoclass('org.test.bughunter.VpnEngine')))
            else:
                si = Intent(activity, autoclass('org.test.bughunter.VpnEngine'))
                si.setAction("STOP"); activity.startService(si)
        except Exception as e: self.add_log(f"Android API Error: {e}")

    def run_engine(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_tunnel())

    async def async_tunnel(self):
        server = await asyncio.start_server(self.socks_handler, '127.0.0.1', 1080)
        async with server:
            while self.connected: await asyncio.sleep(0.5)
            server.close()

    async def socks_handler(self, reader, writer):
        try:
            await reader.readexactly(2); writer.write(b"\x05\x00"); await writer.drain()
            req = await reader.readexactly(4); _, _, _, atyp = struct.unpack("!BBBB", req)
            if atyp == 1: addr = socket.inet_ntoa(await reader.readexactly(4))
            elif atyp == 3: addr = (await reader.readexactly((await reader.readexactly(1))[0])).decode()
            port = struct.unpack("!H", await reader.readexactly(2))[0]
            writer.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00"); await writer.drain()

            # VLESS Tunnel (Verification)
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname, ssl_ctx.verify_mode = False, ssl.CERT_NONE
            ssl_ctx.set_alpn_protocols(['http/1.1'])
            headers = {"Host": ACTUAL_SERVER, "Upgrade": "websocket", "Connection": "Upgrade"}

            async with aiohttp.ClientSession() as sess:
                async with sess.ws_connect(f"https://{CONNECT_IP}:{PORT}{WS_PATH}", headers=headers, ssl=ssl_ctx, server_hostname=self.selected_bug) as ws:
                    # ONLY UPDATE STATUS AFTER SUCCESSFUL WEBSOCKET UPGRADE
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'CONNECTED'))
                    self.add_log(f"Tunnel Established: {addr}:{port} | SNI: {self.selected_bug}")
                    
                    async def up():
                        first = True
                        while self.connected:
                            data = await reader.read(16384)
                            if not data: break
                            if first:
                                h = struct.pack("!B16sBBH", 0, uuid.UUID(USER_UUID).bytes, 0, 1, port)
                                h += (b"\x01" + socket.inet_aton(addr)) if atyp == 1 else (b"\x02" + len(addr).to_bytes(1, 'big') + addr.encode())
                                await ws.send_bytes(h + data); first = False
                            else: await ws.send_bytes(data)

                    async def down():
                        first_res = True
                        async for msg in ws:
                            if not self.connected: break
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                writer.write(msg.data[2:] if first_res else msg.data)
                                await writer.drain(); first_res = False

                    await asyncio.gather(up(), down())
        except: pass
        finally: writer.close()

if __name__ == "__main__":
    BugHunterApp().run()
