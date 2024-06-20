import os

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from kivy.lang import Builder

class DashboardScreen(Screen):
    Window.clearcolor = (30/255,129/255,176/255,0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        #Dashboard
        kv_file_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'image.kv')
        img = Builder.load_file(kv_file_path)
        layout.add_widget(img)

        chat_button = Button(
            text='Therapist',
            size_hint=(1, 0.5),
            size=(200, 50),
            font_size=20,
            on_release=lambda x: self.load_and_switch_to_chat()
        )
        layout.add_widget(chat_button)

        # To-Do List button
        todo_list_button = Button(
            text='To-Do List',
            size_hint=(1, 0.5),
            size=(200, 50),
            font_size=20,
            on_release=lambda x: self.load_and_switch_to_todo_list()
        )
        layout.add_widget(todo_list_button)

        kv_file_path_exit_button = os.path.join(os.path.dirname(__file__), '..', 'kv', 'ExitButton.kv')
        exit_button = Builder.load_file(kv_file_path_exit_button)
        layout.add_widget(exit_button)


        self.add_widget(layout)


    def load_and_switch_to_todo_list(self):
        todo_screen = self.manager.get_screen('todo')

        todo_screen.load_tasks_from_s3()
        self.switch_screen('todo')

    def load_and_switch_to_chat(self):
        chat_screen = self.manager.get_screen('chat')

        # Initialize S3 client before switching
        config = self.manager.config
        aws_access_key_id = config['aws_access_key_id']
        aws_secret_key = config['aws_secret_key']
        aws_region = config['aws_region']

        chat_screen.initialize_s3_client(aws_access_key_id, aws_secret_key, aws_region)

        popup = Popup(title='Dislaimer', content=Label(text='This app is not meant to \nsubstitute medical advice.'),
                      size_hint=(None, None), size=(200, 200))
        popup.open()

        chat_screen.load_chat_history()
        self.switch_screen('chat')

    def switch_screen(self, screen_name):
        self.manager.current = screen_name