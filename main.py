from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from threading import Thread

class HunterUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.core = BugHunterCore() # The class from above
        
        self.btn = Button(text="START BUG HUNT", size_hint_y=0.1)
        self.btn.bind(on_press=self.start_hunt)
        
        self.log_area = Label(text="Ready...", size_hint_y=None, halign='left', valign='top')
        self.log_area.bind(size=self.log_area.setter('text_size'))
        
        self.scroll = ScrollView()
        self.scroll.add_widget(self.log_area)
        
        self.add_widget(self.btn)
        self.add_widget(self.scroll)

    def log(self, text):
        self.log_area.text += f"\n{text}"

    def start_hunt(self, instance):
        self.log_area.text = "[*] Starting..."
        Thread(target=self.run_logic).start()

    def run_logic(self):
        ip = self.core.get_local_ip()
        if not ip:
            self.log("[!] No WiFi detected")
            return
        
        portal = self.core.detect_portal(ip)
        self.log(f"[+] Portal: {portal}")
        
        domains = self.core.extract_domains(portal)
        self.log(f"[*] Found {len(domains)} domains. Resolving...")
        
        ips = set()
        for d in domains:
            try: ips.add(socket.gethostbyname(d))
            except: continue
            
        for target in ips:
            self.log(f"[~] Testing {target}...")
            if self.core.check_vless(target):
                self.log(f"    [✔] WORKING: {target}")

class BugHunterApp(App):
    def build(self):
        return HunterUI()

if __name__ == "__main__":
    BugHunterApp().run()
