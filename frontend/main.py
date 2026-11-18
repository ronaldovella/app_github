import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from screens.chat_screen import ChatScreen

Window.size = (320, 533)


class AAsosApp(App):
    def build(self):
        self.title = "AASOS - Apoio e Acolhimento"
        sm = ScreenManager()
        sm.add_widget(ChatScreen(name='chat'))
        return sm


if __name__ == '__main__':
    AAsosApp().run()