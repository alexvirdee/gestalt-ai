import os
from dotenv import load_dotenv
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.scrollview import ScrollView
# from kivy.uix.textinput import TextInput
# from kivy.uix.button import Button
# from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.app import App

import openai
# from kivy.lang import Builder
# import boto3
# from botocore.exceptions import ClientError
# from kivy.uix.popup import Popup

from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.chat import ChatScreen
from screens.todo import ToDoScreen


# cognito_client = boto3.client('cognito-idp', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)
# s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

# openai.api_key = ""
# modelT = 'gpt-3.5-turbo'
chat_history = []
# current_user = ''

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
        # Create the ScreenManager
        sm = GestaltScreenManager(config)

        # Add screens to the ScreenManager
        # sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ToDoScreen(name='todo'))

        return sm

    def on_start(self):
        chat_screen = self.root.get_screen('chat')
        chat_screen.chat_history = chat_history


if __name__ == '__main__':
    Gestalt().run()
