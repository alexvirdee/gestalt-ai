from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

class DashboardScreen(Screen):
    Window.clearcolor = (30/255,129/255,176/255,0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=10,)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        #Dashboard
        img = Builder.load_file('image.kv')
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

        exit_button = Builder.load_file('ExitButton.kv')
        layout.add_widget(exit_button)


        self.add_widget(layout)


    def load_and_switch_to_todo_list(self):
        todo_screen = self.manager.get_screen('todo')

        todo_screen.load_tasks_from_s3()
        self.switch_screen('todo')

    def load_and_switch_to_chat(self):
        chat_screen = self.manager.get_screen('chat')
        popup = Popup(title='Dislaimer', content=Label(text='This app is not meant to \nsubstitute medical advice.'),
                      size_hint=(None, None), size=(200, 200))
        popup.open()

        chat_screen.load_chat_history()
        self.switch_screen('chat')

    def switch_screen(self, screen_name):
        self.manager.current = screen_name