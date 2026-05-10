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

# ================= HARDCODED VLESS CONFIG =================
USER_UUID       = "4224f578-6c71-4cf2-ae77-3cf1d8878fed"
ACTUAL_SERVER   = "web.chomba.tech"
WS_PATH         = "/vless"
CONNECT_IP      = "104.26.3.143" 
PORT            = 443
# ==========================================================

class BugHunterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        
        self.scanning = False
        self.connected = False
        self.selected_bug = ACTUAL_SERVER # Default bug
        
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
        self.top_bar = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), md_bg_color=(0.1, 0.1, 0.1, 1))
        
        self.vpn_btn = MDFlatButton(text="VPN", theme_text_color="Custom", text_color=(1,1,1,1), on_release=lambda x: self.switch_screen("vpn"))
        self.logs_btn = MDFlatButton(text="LOGS", theme_text_color="Custom", text_color=(1,1,1,1), on_release=lambda x: self.switch_screen("logs"))
        self.copy_btn = MDIconButton(icon="content-copy", theme_text_color="Custom", text_color=(0,1,0,1), on_release=self.copy_logs)

        self.top_bar.add_widget(self.vpn_btn)
        self.top_bar.add_widget(self.logs_btn)
        self.top_bar.add_widget(Widget())
        self.top_bar.add_widget(self.copy_btn)

        # --- SCREENS ---
        self.sm = ScreenManager()
        
        # VPN SCREEN
        self.vpn_screen = Screen(name="vpn")
        vpn_layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.status_label = MDLabel(text="DISCONNECTED", halign="center", font_style="H4", theme_text_color="Error")
        self.bug_info = MDLabel(text=f"Active Bug: {self.selected_bug}", halign="center", font_style="Caption", theme_text_color="Secondary")
        
        self.connect_btn = MDRaisedButton(text="CONNECT", size_hint=(.8, None), pos_hint={"center_x": .5}, md_bg_color=(0, .6, 0, 1), on_release=self.toggle_vpn)
        self.scan_btn = MDRaisedButton(text="START SCAN", size_hint=(.8, None), pos_hint={"center_x": .5}, on_release=self.toggle_scan)
        
        vpn_layout.add_widget(Widget())
        vpn_layout.add_widget(self.status_label)
        vpn_layout.add_widget(self.bug_info)
        vpn_layout.add_widget(self.connect_btn)
        vpn_layout.add_widget(self.scan_btn)
        vpn_layout.add_widget(Widget())
        self.vpn_screen.add_widget(vpn_layout)

        # LOGS SCREEN
        self.logs_screen = Screen(name="logs")
        self.log_scroll = MDScrollView()
        self.log_text = MDLabel(text="--- Debug Logs ---\n", size_hint_y=None, halign="left", font_style="Caption", theme_text_color="Secondary", padding=[dp(10), dp(10)])
        self.log_text.bind(texture_size=self.log_text.setter('size'))
        self.log_scroll.add_widget(self.log_text)
        self.logs_screen.add_widget(self.log_scroll)

        self.sm.add_widget(self.vpn_screen)
        self.sm.add_widget(self.logs_screen)

        self.right_content.add_widget(self.top_bar)
        self.right_content.add_widget(self.sm)
        self.main_container.add_widget(self.left_rail)
        self.main_container.add_widget(self.right_content)
        self.main_screen_wrapper.add_widget(self.main_container)
        self.outer_sm.add_widget(self.main_screen_wrapper)
        self.nav_layout.add_widget(self.outer_sm)

        # SIDE MENU (Bug Setup)
        self.nav_drawer = MDNavigationDrawer(radius=(0, dp(16), dp(16), 0))
        drawer_box = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        drawer_box.add_widget(MDLabel(text="Settings", font_style="H6"))
        self.bug_input = MDTextField(hint_text="Enter Bug Host", text=ACTUAL_SERVER)
        drawer_box.add_widget(self.bug_input)
        drawer_box.add_widget(MDRaisedButton(text="APPLY BUG", on_release=self.apply_manual_bug))
        drawer_box.add_widget(Widget())
        self.nav_drawer.add_widget(drawer_box)
        self.nav_layout.add_widget(self.nav_drawer)

        return self.nav_layout

    def add_log(self, message):
        def update_label(dt):
            self.log_text.text += f"[*] {message}\n"
        Clock.schedule_once(update_label)

    def copy_logs(self, instance):
        Clipboard.copy(self.log_text.text)
        self.add_log("Logs copied to clipboard.")

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

    def apply_manual_bug(self, instance):
        self.selected_bug = self.bug_input.text
        self.bug_info.text = f"Active Bug: {self.selected_bug}"
        self.add_log(f"Manual Bug Host set: {self.selected_bug}")
        self.nav_drawer.set_state("close")

    # ================= SCANNER LOGIC (EXACT AS PROVIDED) =================
    def toggle_scan(self, instance):
        if not self.scanning:
            self.scanning = True
            self.scan_btn.text = "STOP SCAN"
            self.status_label.text = "SCANNING..."
            threading.Thread(target=self.run_scanner, daemon=True).start()
        else:
            self.scanning = False

    def run_scanner(self):
        BASH_REGEX = r'(?i)((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|me|be))'
        EXCLUDE_FILTER = r'\.(jpg|jpeg|png|gif|ico|svg|css|js|mp4|woff|woff2|ttf)$'
        try:
            self.add_log("Scanning for Captive Portal...")
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5, allow_redirects=False)
            portal = r.headers.get('Location')
            if not portal:
                self.add_log("No Portal found.")
                Clock.schedule_once(lambda dt: self.set_status("NO PORTAL", "Error"))
                return
            
            self.add_log(f"Mirroring Portal: {urlparse(portal).netloc}")
            res = requests.get(portal, timeout=10)
            content = res.text
            
            # JS Mirroring logic
            js_paths = re.findall(r'src=["\'](.*\.js.*?)["\']', content)
            for path in js_paths:
                if not self.scanning: break
                try:
                    js_url = urljoin(portal, path)
                    self.add_log(f"Mirroring JS: {path.split('/')[-1]}")
                    content += "\n" + requests.get(js_url, timeout=5).text
                except: pass

            matches = list(set(re.findall(BASH_REGEX, content)))
            valid_bugs = []
            for m in matches:
                if not self.scanning: break
                if not re.search(EXCLUDE_FILTER, m, re.IGNORECASE):
                    self.add_log(f"Testing Bug Host: {m}")
                    if self.handshake_test(m):
                        valid_bugs.append(m)
                        self.add_log(f"SUCCESS: {m} (101 OK)")
            
            if valid_bugs:
                self.selected_bug = valid_bugs[0]
                self.add_log(f"Selected Bug: {self.selected_bug}")
            
            Clock.schedule_once(lambda dt: self.set_status("SCAN COMPLETE", "Primary"))
        except Exception as e:
            self.add_log(f"Scanner error: {e}")
            Clock.schedule_once(lambda dt: self.set_status("SCAN FAILED", "Error"))
        finally:
            self.scanning = False
            Clock.schedule_once(lambda dt: setattr(self.scan_btn, 'text', 'START SCAN'))

    def handshake_test(self, bug):
        header = f"GET {WS_PATH} HTTP/1.1\r\nHost: {ACTUAL_SERVER}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n"
        try:
            s = socket.create_connection((bug, 443), timeout=3)
            ss = ssl._create_unverified_context().wrap_socket(s, server_hostname=ACTUAL_SERVER)
            ss.send(header.encode())
            return "101" in ss.recv(1024).decode(errors='ignore')
        except: return False

    def set_status(self, text, color):
        self.status_label.text = text
        self.status_label.theme_text_color = color

    # ================= VPN ENGINE (VLESS + ANDROID BRIDGE) =================
    def toggle_vpn(self, instance):
        if not self.connected:
            self.connected = True
            self.connect_btn.text = "STOP"
            self.connect_btn.md_bg_color = (1, 0, 0, 1)
            self.set_status("CONNECTING...", "Primary")
            self.start_android_service()
            threading.Thread(target=self.run_async_engine, daemon=True).start()
        else:
            self.connected = False
            self.connect_btn.text = "CONNECT"
            self.connect_btn.md_bg_color = (0, .6, 0, 1)
            self.set_status("DISCONNECTED", "Error")
            self.stop_android_service()

    def start_android_service(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                VpnService = autoclass('android.net.VpnService')
                Intent = autoclass('android.content.Intent')
                
                activity = PythonActivity.mActivity
                prep = VpnService.prepare(activity)
                if prep: activity.startActivityForResult(prep, 0)
                
                service = Intent(activity, autoclass('org.test.bughunter.VpnEngine'))
                activity.startService(service)
                self.add_log("Android VpnService Started.")
            except Exception as e:
                self.add_log(f"Java Bridge Error: {e}")

    def stop_android_service(self):
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            service = Intent(activity, autoclass('org.test.bughunter.VpnEngine'))
            service.setAction("STOP")
            activity.startService(service)

    def run_async_engine(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.engine_main())

    async def engine_main(self):
        server = await asyncio.start_server(self.socks_logic, '127.0.0.1', 1080)
        async with server:
            while self.connected:
                await asyncio.sleep(0.5)
            server.close()

    async def socks_logic(self, reader, writer):
        try:
            # SOCKS5 Handshake
            await reader.readexactly(2)
            writer.write(b"\x05\x00")
            await writer.drain()

            # Connection Request
            req = await reader.readexactly(4)
            _, _, _, atyp = struct.unpack("!BBBB", req)
            if atyp == 1:
                addr = socket.inet_ntoa(await reader.readexactly(4))
            elif atyp == 3:
                addr_len = (await reader.readexactly(1))[0]
                addr = (await reader.readexactly(addr_len)).decode()
            port = struct.unpack("!H", await reader.readexactly(2))[0]
            writer.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
            await writer.drain()

            # VLESS Tunneling
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname, ssl_ctx.verify_mode = False, ssl.CERT_NONE
            ssl_ctx.set_alpn_protocols(['http/1.1'])

            ws_url = f"https://{CONNECT_IP}:{PORT}{WS_PATH}"
            headers = {"Host": ACTUAL_SERVER, "Upgrade": "websocket", "Connection": "Upgrade"}

            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url, headers=headers, ssl=ssl_ctx, server_hostname=self.selected_bug) as ws:
                    # Update UI to connected on first success
                    Clock.schedule_once(lambda dt: self.set_status("CONNECTED", "Primary"))
                    self.add_log(f"[+] Tunnel Connected: {addr}:{port} | SNI: {self.selected_bug}")
                    
                    async def up():
                        first = True
                        while self.connected:
                            data = await reader.read(16384)
                            if not data: break
                            if first:
                                uid = uuid.UUID(USER_UUID).bytes
                                h = struct.pack("!B16sBBH", 0, uid, 0, 1, port)
                                if atyp == 1: h += b"\x01" + socket.inet_aton(addr)
                                else: h += b"\x02" + len(addr).to_bytes(1, 'big') + addr.encode()
                                await ws.send_bytes(h + data)
                                first = False
                            else:
                                await ws.send_bytes(data)

                    async def down():
                        first_res = True
                        async for msg in ws:
                            if not self.connected: break
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                writer.write(msg.data[2:] if first_res else msg.data)
                                await writer.drain()
                                first_res = False

                    await asyncio.gather(up(), down())
        except: pass
        finally: writer.close()

if __name__ == "__main__":
    BugHunterApp().run()
