import os
from dotenv import load_dotenv

from kivy.uix.screenmanager import ScreenManager
from kivy.app import App

from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.chat import ChatScreen
from screens.todo import ToDoScreen


chat_history = []

# Load environment variables from .env file
load_dotenv()

# Create a configuration dictionary
config = {
    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'aws_secret_key': os.getenv('AWS_SECRET_KEY'),
    'aws_region':     os.getenv('AWS_REGION'),
    'open_ai_api_key': os.getenv('OPEN_AI_API_KEY')
}

class GestaltScreenManager(ScreenManager):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

class Gestalt(App):
    def build(self):
        current_user = None

        # Create the ScreenManager
        sm = GestaltScreenManager(config)

        # Add screens to the ScreenManager
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ToDoScreen(name='todo'))

        return sm

    def on_start(self):
        chat_screen = self.root.get_screen('chat')
        chat_screen.chat_history = chat_history


if __name__ == '__main__':
    Gestalt().run()