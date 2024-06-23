from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from botocore.exceptions import ClientError

import boto3

current_user = ''

class ToDoScreen(Screen):

   def on_enter(self):
      # Load todos
      self.load_tasks_from_s3

   def __init__(self, **kwargs):
       super(ToDoScreen, self).__init__(**kwargs)
       self.todo_list = []

       layout = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint=(1, 1),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})

       exit_button = Button(text="Exit", size_hint=(None, None), width=100, height=50)
       exit_button.bind(on_press=lambda x: self.switch_to_dashboard())

       self.task_input = TextInput(hint_text="Enter a task", size_hint=(1, None), height=50)
       add_button = Button(text="Add Task", size_hint=(1, None), height=50)  # Adjusted size
       add_button.bind(on_press=self.add_task)

       # Create a ScrollView
       task_container_scrollview = ScrollView()

       # Create a new BoxLayout for the task_container with reversed orientation
       self.task_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, padding=5)

       task_container_scrollview.add_widget(self.task_container)

       layout.add_widget(exit_button)
       layout.add_widget(self.task_input)
       layout.add_widget(add_button)
       layout.add_widget(task_container_scrollview)  # Add the ScrollView

       self.add_widget(layout)
       # Load tasks from the file at the start
       #self.load_tasks_from_s3()

   def add_task_to_list(self, task_text):
       task_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=30)
       task_label = Label(text=task_text)
       remove_button = Button(text="Remove")
       remove_button.bind(on_press=lambda x: self.remove_task(task_layout, task_text))
       task_layout.add_widget(task_label)
       task_layout.add_widget(remove_button)

       # Insert new tasks at the top
       self.task_container.add_widget(task_layout, index=0)
       self.todo_list.append(task_text)

       # Update the height of the task container for scrolling
       self.task_container.height += task_layout.height
       self.save_tasks_to_s3()

   def add_task(self, instance):
       task_text = self.task_input.text
       if task_text:
           self.add_task_to_list(task_text)
           self.save_tasks_to_s3()
           self.task_input.text = ""

   def remove_task(self, task_layout, task_text):
       if task_text in self.todo_list:
           self.todo_list.remove(task_text)
       self.task_container.remove_widget(task_layout)
       self.task_container.height -= task_layout.height
       self.save_tasks_to_s3()
    
   def initialize_s3_client(self, aws_access_key_id, aws_secret_key, aws_region):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_key,
            region_name="us-east-1"
    )

   def load_tasks_from_s3(self):
       app = App.get_running_app()
       current_user = app.current_user
       print("current user load: " + current_user)
       try:

           response = self.s3_client.get_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ToDoList.txt')
           tasks = response['Body'].read().decode('utf-8').splitlines()
           for task in tasks:
               if task:
                   self.add_task_to_list(task)
       except ClientError as e:
           print(f"Error loading tasks from S3: {e}")

   def save_tasks_to_s3(self):
       app = App.get_running_app()
       current_user = app.current_user
       try:
           # Save current tasks to a data structure
           current_tasks = '\n'.join(self.todo_list)
           print("current user save: " + current_user)
           # Delete the existing ToDoList.txt file in S3
           self.s3_client.delete_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ToDoList.txt')

           # Upload the updated tasks to S3
           self.s3_client.put_object(Bucket='gestaltfilestorage', Key=f'{app.current_user}ToDoList.txt',
                                Body=current_tasks)
       except ClientError as e:
           print(f"Error saving tasks to S3: {e}")

   def switch_to_dashboard(self):
       self.manager.current = 'dashboard'