from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class BugHunterApp(MDApp):
    def build(self):
        # The main screen
        screen = MDScreen()
        
        # A layout to center the button
        layout = MDBoxLayout(orientation='vertical', spacing=20, adaptive_size=True, pos_hint={"center_x": .5, "center_y": .5})
        
        # The button
        btn = MDRaisedButton(
            text="Press Me",
            on_release=self.button_pressed
        )
        
        layout.add_widget(btn)
        screen.add_widget(layout)
        return screen

    def button_pressed(self, instance):
        print("Button was pressed!")
        instance.text = "You pressed it! 🎉"

if __name__ == "__main__":
    BugHunterApp().run()
