from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from botocore.exceptions import ClientError

import boto3

import openai

chat_history = []
# current_user = ''


class ChatScreen(Screen):
    
    def on_enter(self):
      # Load chat history when the screen is entered
      self.load_chat_history()
      config = self.manager.config
      openai_key = config['open_ai_api_key']
      openai.api_key = openai_key
    #   print("currentUser =", current_user)

    def __init__(self, **kwargs):
     super().__init__(**kwargs)

     # Initialize s3_client with None
     self.s3_client = None

     # Load chat history from a text file when the screen is opened

     layout = BoxLayout(orientation='vertical')

     # Chat history (center part) using ScrollView and reversed BoxLayout
     chat_history_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
     chat_history_layout.bind(minimum_height=chat_history_layout.setter('height'))

     chat_history_scroll_view = ScrollView()
     chat_history_scroll_view.add_widget(chat_history_layout)

     layout.add_widget(chat_history_scroll_view)

     # User input and send button (right part)
     user_input_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)

     user_input = TextInput(multiline=False, font_size=20, hint_text = "Talk about your day...")
     user_input_layout.add_widget(user_input)

     send_button = Button(text='Send', size_hint=(None, None), size=(100, 50), font_size=20,
                          on_press=lambda x: self.send_message(chat_history_layout, user_input.text, user_input))
     user_input.text = ''
     user_input_layout.add_widget(send_button)

     layout.add_widget(user_input_layout)

     # Exit button
     exit_button = Button(text='Exit', size_hint=(None, None), size=(100, 50), font_size=20,
                          on_press=lambda x: self.switch_to_dashboard())
     layout.add_widget(exit_button)

     self.add_widget(layout)

    def initialize_s3_client(self, aws_access_key_id, aws_secret_key, aws_region):
        print("s3 initialized")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_key,
            region_name="us-east-1"
    )

    def load_chat_history(self):
     app = App.get_running_app()
     current_user = app.current_user
     if self.s3_client is None:
        raise AttributeError("S3 client is not initialized.")

     try:
         response = self.s3_client.get_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ChatHistory.txt')
         lines = response['Body'].read().decode('utf-8').splitlines()
         for line in lines:
             if line.startswith('You: '):
                 user_message = {"role": "user", "content": line[5:]}
                 chat_history.append(user_message)
             elif line.startswith('Bot: '):
                 bot_message = {"role": "assistant", "content": line[5:]}
                 chat_history.append(bot_message)
         print(chat_history)
     except ClientError as e:
         print(f"Error loading chat history from S3: {e}")

    def send_message(self, chat_history_layout, message, user_input):
     # Append user message to chat history
     user_message = {"role": "user", "content": message}
     chat_history.append(user_message)

     # Append user message to chat history
     user_message_text = f'You: {message}\n'
     #self.chat_history.append(user_message_text) #THIS LINE IS THE ISSUE
     chat_label = Label(text=user_message_text, font_size=20, halign='right', size_hint_y=None,
                        text_size=(self.width, None))
     chat_label.size_hint_y = None
     chat_label.bind(texture_size=chat_label.setter('size'))
     chat_history_layout.add_widget(chat_label)

     user_input.text = ''

     # Generate chatbot's response using GPT-2
     bot_response = self.generate_response(chat_history)

     # Append chatbot's response to chat history
     bot_message = f'Bot: {bot_response}\n'
     #self.chat_history.append(bot_message) #THIS LINE TOO
     bot_chat_label = Label(text=bot_message, font_size=20, halign='left', size_hint_y=None,
                            text_size=(self.width, None))
     bot_chat_label.size_hint_y = None
     bot_chat_label.bind(texture_size=bot_chat_label.setter('size'))
     chat_history_layout.add_widget(bot_chat_label)

     # Save the entire chat dialogue to a text file
     self.save_chat_history(chat_history)

     # Scroll to the bottom only if already at the bottom
     chat_history_scroll_view = chat_history_layout.parent
     if chat_history_scroll_view.scroll_y == 0:
         chat_history_scroll_view.scroll_y = 0

     # Trigger layout update to prevent messages from sliding upwards
     chat_history_layout.do_layout()

     # Adjust the chat history layout to display the latest messages at the bottom
     chat_history_layout.height = sum(label.height for label in chat_history_layout.children) + (
             len(chat_history_layout.children) - 1) * chat_history_layout.spacing

    def save_chat_history(self, chat_hist):
     if self.s3_client is None:
        raise AttributeError("S3 client is not initialized.")
     
     try:
         app = App.get_running_app()
         current_user = app.current_user
         # Save the entire chat history to a string

         chat_history_str = ''
         for message in chat_hist:
             if message["role"] == "user":
                 chat_history_str += f'You: {message["content"]}\n'
             elif message["role"] == "assistant":
                 chat_history_str += f'Bot: {message["content"]}\n'

         # Delete the existing ChatHistory.txt file in S3
         self.s3_client.delete_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ChatHistory.txt')

         # Upload the updated chat history to S3
         self.s3_client.put_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ChatHistory.txt',
                              Body=chat_history_str)
     except ClientError as e:
         print(f"Error saving chat history to S3: {e}")

    def generate_response(self, chat_history):

        # Format chat history for OpenAI API
        instructions = "You are a therapist and the user is having a session with you.\
        Also, if someone is stressed about a workload, suggest the To-Do list feature in the Gestalt app(which you are an element of. \
        Give more advice rather than asking questions, although questions are ok. \
        Try to make your responses concise and don't use lists unless absolutely neccesary."

        messages = [{"role": "system", "content": instructions}]
        messages.extend(chat_history)  # Include user and assistant messages

        # Generate chatbot's response using OpenAI ChatCompletion model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= messages
        )
        chat_history.append({"role": "assistant", "content": response.choices[0].message['content'].strip()})
        return response.choices[0].message['content'].strip()


    def switch_to_dashboard(self):
        self.manager.current = 'dashboard'