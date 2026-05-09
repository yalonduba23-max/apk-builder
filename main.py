import os
import re
import socket
import requests
import traceback
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.utils import platform

# --- ANDROID PERMISSIONS ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class ConsoleUI(BoxLayout):
    # ... (Keep the same Background and Log code from my previous response) ...
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.scroll = ScrollView(do_scroll_x=False)
        self.log_label = Label(text="[b][SYSTEM][/b] Initializing Storage...", markup=True, size_hint_y=None, halign='left', valign='top', color=(0, 1, 0, 1))
        self.log_label.bind(size=self._update_text_size)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)

    def _update_rect(self, instance, value): self.rect.pos, self.rect.size = instance.pos, instance.size
    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width * 0.98, None)
        instance.height = max(instance.texture_size[1], self.scroll.height)

    def log(self, message, color="00FF00"):
        def _append(dt): 
            self.log_label.text += f"\n[[{color}]] {message}"
            self.scroll.scroll_y = 0
        Clock.schedule_once(_append)

class BugHunterApp(App):
    def build(self):
        self.ui = ConsoleUI()
        return self.ui

    def on_start(self):
        # 1. Request Permissions on Startup
        if platform == 'android':
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        
        Thread(target=self.safe_run, daemon=True).start()

    def get_save_path(self):
        """Returns the best path to save files on Android vs PC"""
        if platform == 'android':
            # This saves to /storage/emulated/0/Android/data/package.name/files
            # It's the only place Android 11+ allows writing easily
            return self.user_data_dir
        return os.getcwd()

    def safe_run(self):
        try:
            self.run_logic()
        except Exception:
            self.ui.log(traceback.format_exc(), "FF0000")

    def run_logic(self):
        path = self.get_save_path()
        filename = os.path.join(path, "domains.txt")
        
        self.ui.log(f"[*] Storage Path: {path}", "00FFFF")

        # --- EXAMPLE FILE WRITE ---
        self.ui.log("[*] Saving test data...")
        try:
            with open(filename, "w") as f:
                f.write("test_domain.com\nexample.org\n")
            self.ui.log(f"[✔] Successfully saved to:\n{filename}", "FFFF00")
        except Exception as e:
            self.ui.log(f"[!] Write Failed: {e}", "FF0000")

        # --- PORTAL LOGIC ---
        self.ui.log("[*] Starting Phase 1...", "00FFFF")
        # (Insert your requests and re logic here)
        
        # When you find domains, write them using the 'filename' path
        # with open(filename, "a") as f: ...

if __name__ == "__main__":
    BugHunterApp().run()
