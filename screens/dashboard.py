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
            on_release=lambda x: self.load_and_switch_to_screen('chat', 'load_chat_history')
        )
        layout.add_widget(chat_button)

        # To-Do List button
        todo_list_button = Button(
            text='To-Do List',
            size_hint=(1, 0.5),
            size=(200, 50),
            font_size=20,
            on_release=lambda x: self.load_and_switch_to_screen('todo', 'load_tasks_from_s3')
        )
        layout.add_widget(todo_list_button)

        kv_file_path_exit_button = os.path.join(os.path.dirname(__file__), '..', 'kv', 'ExitButton.kv')
        exit_button = Builder.load_file(kv_file_path_exit_button)
        layout.add_widget(exit_button)


        self.add_widget(layout)

    def initialize_s3_client(self, screen):
        config = self.manager.config
        aws_access_key_id = config['aws_access_key_id']
        aws_secret_key = config['aws_secret_key']
        aws_region = config['aws_region']

        screen.initialize_s3_client(aws_access_key_id, aws_secret_key, aws_region)

    def load_and_switch_to_screen(self, screen_name, load_method_name):
        screen = self.manager.get_screen(screen_name)
        self.initialize_s3_client(screen)

        # Call specified load method on the screen
        load_method = getattr(screen, load_method_name)
        load_method()

        if screen_name == 'chat':
            popup = Popup(title='Dislaimer', content=Label(text='This app is not meant to \nsubstitute medical advice.'),
                      size_hint=(None, None), size=(200, 200))
            popup.open()
        
        self.switch_screen(screen_name)

    def switch_screen(self, screen_name):
        self.manager.current = screen_name