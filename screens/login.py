import os

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.lang import Builder

from botocore.exceptions import ClientError

import boto3


class LoginScreen(Screen):
  
  def on_enter(self):
      # Access the config through the parent screen manager
      config = self.manager.config
      aws_access_key_id = config['aws_access_key_id']
      aws_secret_key = config['aws_secret_key']
      aws_region = config['aws_region']

      self.cognito_client = boto3.client('cognito-idp', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_key, region_name=aws_region)

      self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_key, region_name=aws_region)

  def __init__(self, **kwargs):
      super().__init__(**kwargs)

      layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.6, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.5})
      
      kv_file_path = os.path.join(os.path.dirname(__file__), '..', 'kv', 'image.kv')
      img = Builder.load_file(kv_file_path)
      layout.add_widget(img)

      username_label = Label(text='Username:', size_hint_y=None, height=40)
      self.username_input = TextInput(multiline=False, size_hint_y=None, height=50, size_hint_x=1)

      password_label = Label(text='Password:', size_hint_y=None, height=40)
      self.password_input = TextInput(password=True, multiline=False, size_hint_y=None, height=50, size_hint_x=1)

      login_button = Button(text='Login', on_press=self.login, size_hint_y=None, height=50, size_hint_x=1)
      sign_up_button = Button(text='Sign Up', on_press=lambda x: self.sign_up(), size_hint_y=None, height=50, size_hint_x=1)

      layout.add_widget(username_label)
      layout.add_widget(self.username_input)
      layout.add_widget(password_label)
      layout.add_widget(self.password_input)
      layout.add_widget(login_button)
      layout.add_widget(sign_up_button)

      self.add_widget(layout)

  def login(self, instance):
      global current_user
      username = self.username_input.text
      password = self.password_input.text
      current_user = username
      print("current user: " + current_user)
      if self.cognito_login(username, password):
          # Navigate to the dashboard on successful login
          self.manager.current = 'dashboard'

      else:
          # Display an error message in a popup on login failure
          popup = Popup(title='Login Error', content=Label(text='Invalid username or password.'),
                        size_hint=(None, None), size=(600, 500))
          popup.open()

  def cognito_login(self, username, password):
      try:
          response = self.cognito_client.initiate_auth(
              ClientId='3rscvq1mrc51g92831osg1sgr7',
              AuthFlow='USER_PASSWORD_AUTH',
              AuthParameters={
                  'USERNAME': username,
                  'PASSWORD': password,
              },
          )
          return True
      except ClientError as e:
          print(f"Error during login: {e.response['Error']['Message']}")
          return False

  def sign_up(self):
      global current_user
      username = self.username_input.text
      password = self.password_input.text
      self.username = username
      current_user = username

      if self.cognito_sign_up(username, password):
          # Display a popup for entering the confirmation code
          self.show_verification_popup()

      else:
          # Display an error message in a popup on sign-up failure
          popup = Popup(title='Sign-Up Error',
                        content=Label(text='Failed to sign up.\nPlease check your input and try again.'),
                        size_hint=(None, None), size=(600, 500))
          popup.open()

  def show_verification_popup(self):
      # Create a popup with a TextInput for entering the verification code
      verification_input = TextInput(hint_text='Enter verification code', multiline=False)
      verification_popup = Popup(title='Verification Code',
                                 content=BoxLayout(orientation='vertical'),
                                 size_hint=(None, None), size=(600, 500),
                                 auto_dismiss=False)

      # Create a button to confirm the verification code
      confirm_button = Button(text='Confirm',
                              on_press=lambda x: self.confirm_signup(verification_input.text, verification_popup))
      verification_popup.content.add_widget(confirm_button)

      # Create a button to dismiss the popup
      dismiss_button = Button(text='Dismiss', on_press=verification_popup.dismiss)
      verification_popup.content.add_widget(dismiss_button)

      # Add the verification input to the popup content
      verification_popup.content.add_widget(verification_input)

      verification_popup.open()


  def cognito_sign_up(self, username, password):
      current_user = username
      try:
          response = self.cognito_client.sign_up(
              ClientId='3rscvq1mrc51g92831osg1sgr7',
              Username=username,
              Password=password,
              UserAttributes=[
                  {'Name': 'email', 'Value': username},
              ],
          )
          print("Sign-up successful. Confirmation code sent to:", response['UserConfirmed'])
          current_user = self.username

          self.s3_client.put_object(Bucket='gestaltfilestorage', Key=f'{self.username}ToDoList.txt',
                               Body='')

          self.s3_client.put_object(Bucket='gestaltfilestorage', Key=f'{self.username}ChatHistory.txt',
                               Body='')

          return True

      except ClientError as e:
          print(f"Error during sign-up: {e.response['Error']['Message']}")
          return False



  def confirm_signup(self, verification_code, verification_popup):
      try:
          response = self.cognito_client.confirm_sign_up(
              ClientId='3rscvq1mrc51g92831osg1sgr7',
              Username=self.username,
              ConfirmationCode=verification_code,
          )
          print("Account confirmed successfully.")
          verification_popup.dismiss()

          # Optionally, you can navigate to the dashboard or perform other actions after confirmation
          self.manager.current = 'dashboard'

      except ClientError as e:
          print(f"Error confirming signup: {e.response['Error']['Message']}")
          # Display an error message in the popup on confirmation failure
          error_label = Label(text=f'Error: {e.response["Error"]["Message"]}')
          verification_popup.content.add_widget(error_label)
