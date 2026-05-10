from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivy.uix.widget import Widget
from kivy.metrics import dp

class BugHunterApp(MDApp):
    def build(self):
        self.nav_layout = MDNavigationLayout()
        self.outer_sm = ScreenManager()
        self.main_screen_wrapper = Screen(name="main_wrapper")
        self.main_container = MDBoxLayout(orientation='horizontal')

        # LEFT BLACK RAIL
        self.left_rail = MDBoxLayout(
            orientation='vertical', size_hint_x=None, width=dp(50), 
            md_bg_color=(0, 0, 0, 1), spacing=dp(10), padding=[0, dp(10), 0, 0]
        )
        self.menu_btn = MDIconButton(icon="menu", theme_text_color="Custom", text_color=(1, 1, 1, 1),
                                     on_release=lambda x: self.nav_drawer.set_state("open"))
        self.left_rail.add_widget(self.menu_btn)
        self.left_rail.add_widget(Widget())

        # RIGHT CONTENT
        self.right_content = MDBoxLayout(orientation='vertical')
        self.top_bar = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), md_bg_color=(0, 1, 0, 1))

        self.vpn_btn = MDFlatButton(text="VPN", size_hint=(0.4, 1), theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("vpn"))
        self.logs_btn = MDFlatButton(text="LOGS", size_hint=(0.4, 1), theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("logs"))
        self.gear_btn = MDIconButton(icon="cog", theme_text_color="Custom", text_color=(0,0,0,1), on_release=lambda x: self.switch_screen("settings"))

        self.top_bar.add_widget(self.vpn_btn)
        self.top_bar.add_widget(self.logs_btn)
        self.top_bar.add_widget(self.gear_btn)

        self.sm = ScreenManager()
        self.sm.add_widget(self.create_vpn_screen())
        self.sm.add_widget(Screen(name="logs")) # Placeholder
        self.sm.add_widget(Screen(name="settings")) # Placeholder

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

    def create_vpn_screen(self):
        s = Screen(name="vpn")
        l = MDBoxLayout(orientation='vertical', padding=dp(20))
        l.add_widget(MDRaisedButton(text="SCAN", pos_hint={"center_x": .5}))
        s.add_widget(l)
        return s

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

if __name__ == "__main__":
    BugHunterApp().run()
