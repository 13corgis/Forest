from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import FadeTransition
from kivy.clock import Clock


class ForestApp(MDApp):
    def __init__(self, **kwargs):
        super(ForestApp, self).__init__(**kwargs)
        pass
    
    def build(self):
        self.load_kv_files()
        
        Clock.schedule_once(lambda dt: self.enter_app(), 3)
        
        return Builder.load_file('kv-files/forest.kv')

    def on_start(self):
        pass
    
    # ! Startup Sequence - - - - - - - - - - - -
    def enter_app(self):
        self.root.transition = FadeTransition(duration=2)
        self.root.current = 'startup'
        self.root.transition = FadeTransition(duration=0.3)
        Clock.schedule_once(lambda dt: self.to_login(), 4)

    def to_login(self):
        self.root.current = 'login'
    
    def load_kv_files(self):
        Builder.load_file('kv-files/startup_screen.kv')
        Builder.load_file('kv-files/login_screen.kv')
        Builder.load_file('kv-files/dashboard_screen.kv')
        Builder.load_file('kv-files/setup_screen.kv')
    
    # ! Login Attempt - - - - - - - - - - - -
    def attempt_login(self):
        login_textfield = self.root.get_screen('login').ids.login_textfield
        login_passfield = self.root.get_screen('login').ids.login_passfield

        if login_textfield.text != '' and login_passfield != '':
            if login_textfield.text in self.read_user_database() and self.read_user_database()[
                login_textfield.text] == login_passfield.text:
                print("Logged in successfully")
                self.root.current = 'dashboard'
            else:
                print("Invalid Credentials")

    # ! Signup Attempt - - - - - - - - - - - -
    def attempt_signup(self):
        signup_textfield = self.root.get_screen('login').ids.signup_textfield
        signup_passfield = self.root.get_screen('login').ids.signup_passfield
        signup_cfpassfield = self.root.get_screen('login').ids.signup_cfpassfield

        if signup_textfield.text != '' and signup_passfield.text != '' and signup_cfpassfield.text != '':
            if signup_passfield.text == signup_cfpassfield.text:
                # IF user and pass not in db
                if signup_textfield.text not in self.read_user_database().keys():
                    self.update_user_database(signup_textfield.text, signup_cfpassfield.text)

                    print("Successfully registered")
                    self.root.current = 'login'

                    signup_textfield.text = ''
                    signup_passfield.text = ''
                    signup_cfpassfield.text = ''
                # Else exists
                else:
                    print("Account already exists")
            else:
                print("Passwords do not match")
    
    # ! Database Interactions (Read, Update) - - - - - - - - - - - -
    def read_user_database(self):
        with open('resources/db.txt', mode='r') as file:
            db = {}
            for pair in file.readlines():
                username = pair.split(sep=',')[0]
                password = pair.split(sep=',')[1].strip()
                db[username] = password

            print(db)

            return db

    def update_user_database(self, username, password):
        with open('resources/db.txt', mode='a') as file:
            file.write(f'\n{username},{password}')

ForestApp().run()