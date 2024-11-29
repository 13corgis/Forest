from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import FadeTransition
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import *
from kivymd.uix.relativelayout import MDRelativeLayout

from screeninfo import get_monitors

# ! Configure Window - - - - - - - - - - - -
def init_window():
    # ! Screen Size (NEED TO ADD VALIDATION FOR MULTIPLE SCREENS)

    # Window Size
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    desired_width = 1200
    desired_height = 800

    Window.size = (desired_width, desired_height)
    Window.minimum_width = desired_width
    Window.minimum_height = desired_height

    # Center Window
    x = screen_width // 2 - desired_width // 2
    y = screen_height // 2 - desired_height // 2

    Window.left = x
    Window.top = y

    # Other
    # Window.set_title("Forest")

class ForestApp(MDApp):
    def __init__(self, **kwargs):
        super(ForestApp, self).__init__(**kwargs)
        
        # Member Variables - Background
        self.app_bg = 'resources/test.mp4'
        self.bg_paths = [
            'resources/bg_0.jpg',
            'resources/bg_1.jpg',
            'resources/bg_2.jpg',
            'resources/bg_3.jpg',
            'resources/bg_4.jpg',
            'resources/bg_5.jpg',
            'resources/bg_6.jpg'
        ]
        self.selected_bg = 0
        
        # Member Variables - Menu Components
        self.menu = None
        self.settings_dialog = None
        self.help_dialog = None
    
    def build(self):
        Window.hide()
        
        self.load_kv_files()
        
        Clock.schedule_once(lambda dt: self.enter_app(), 3)
        
        return Builder.load_file('kv-files/forest.kv')

    def on_start(self):
        # ! Initializations - - - - - - - - - - - -
        init_window()
        self.init_bg_images()
        self.init_settings_dialog()
        self.init_help_dialog()
        self.init_profile_menu()
        
        Clock.schedule_once(lambda dt: Window.show(), 0)
    
    # ! Startup Sequence - - - - - - - - - - - -
    def enter_app(self):
        self.root.transition = FadeTransition(duration=2)
        self.root.current = 'startup'
        self.root.transition = FadeTransition(duration=0.3)
        Clock.schedule_once(lambda dt: self.to_login(), 4)

    def to_login(self):
        self.root.current = 'login'

    # ! Change Dashboard Opacity on Dialog.open() and Dialog.dismiss() - - - - - - - - - - - -
    def change_opacity(self):
        components = [
            self.root.get_screen('dashboard').ids.timer_label,
            self.root.get_screen('dashboard').ids.dash_btns
        ]

        for comp in components:
            opacity = comp.opacity
            if opacity == 1 or opacity == 0.6:
                comp.opacity = 0
            elif opacity == 0:
                comp.opacity = 1
    
    # ! Selected Background Tracker - - - - - - - - - - - -
    def manage_background(self, action):

        if action == 'next':
            if self.selected_bg == 6:
                self.selected_bg = 0
            else:
                self.selected_bg += 1
        elif action == 'prev':
            if self.selected_bg == 0:
                self.selected_bg = 6
            else:
                self.selected_bg -= 1

        self.root.get_screen('setup').ids.setup_bg.source = self.bg_paths[self.selected_bg]
    
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
            
    # ! Profile menu > logout - - - - - - - - - - - -
    def logout(self):
        self.root.get_screen('login').ids.login_passfield.text = ''
        self.root.current = 'login'
        self.menu.dismiss()

    # ! Profile Menu - - - - - - - - - - - -
    def open_profile_menu(self):
        self.menu.open()
        
    # ! Initialize Profile Menu - - - - - - - - - - - -
    def init_profile_menu(self):
        self.menu = MDDropdownMenu(
            id='menu',
            caller=self.root.get_screen('dashboard').ids.profile,
            width='120dp',
            position='bottom',
            ver_growth='down',
            hor_growth='right',
            radius=[16, 16, 16, 16],
            opacity=0.85
        )

        settings_item = {
            'text': 'Settings',
            'leading_icon': 'cog',
            'on_press': self.settings_dialog.open
        }
        help_item = {
            'text': 'Help',
            'leading_icon': 'help',
            'on_press': self.help_dialog.open
        }
        logout_item = {
            'text': 'Logout',
            'leading_icon': 'logout',
            'on_press': self.logout
        }

        menu_items = [settings_item, help_item, logout_item]

        for item in menu_items:
            item['md_bg_color'] = (0, 0, 0, 1)
            item['text_color'] = (1, 1, 1, 1)
            item['leading_icon_color'] = (1, 1, 1, 1)
            item['on_release'] = self.menu.dismiss

        self.menu.items = menu_items
    
    # ! Initialize Settings Dialog - - - - - - - - - - - -
    def init_settings_dialog(self):

        self.settings_dialog = MDDialog(
            MDDialogHeadlineText(
                font_style='Headline',
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                text="Settings",
                halign="center"
            ),
            MDDialogContentContainer(
                MDRelativeLayout(
                    Builder.load_file('kv-files/settings_dialog.kv'),
                    size_hint=(None, None),
                    size=(650, 550),
                    pos_hint={'center_x': 0.5, 'center_y': 0.6}
                ),
                size_hint=(1, 1),
                orientation='vertical'
            ),
            size_hint=(None, None),
            size=(650, 550),
            style='outlined',
            theme_bg_color='Custom',
            md_bg_color=(0, 0, 0, 0.0),
            orientation='vertical'
        )

        self.settings_dialog.on_open = self.change_opacity
        self.settings_dialog.on_dismiss = self.change_opacity

    # ! Initialize Help Dialog - - - - - - - - - - - -
    def init_help_dialog(self):
        self.help_dialog = MDDialog(
            MDDialogHeadlineText(
                font_style='Headline',
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                text="About",
                halign="center",
            ),
            MDDialogContentContainer(
                Builder.load_file('kv-files/help_dialog.kv'),
                size_hint=(1, 1),
                orientation='vertical'
            ),
            size_hint=(None, None),
            size=(650, 400),
            style='outlined',
            theme_bg_color='Custom',
            md_bg_color=(0, 0, 0, 0.0),
            orientation='vertical'
        )

        self.help_dialog.on_open = self.change_opacity
        self.help_dialog.on_dismiss = self.change_opacity
    
    # ! Initialize Background Resources - - - - - - - - - - - -
    def init_bg_images(self):
        image = AsyncImage(source=self.app_bg)

        for path in self.bg_paths:
            image = AsyncImage(source=path)
    
    # ! Load kv files - - - - - - - - - - - -
    def load_kv_files(self):
        Builder.load_file('kv-files/startup_screen.kv')
        Builder.load_file('kv-files/login_screen.kv')
        Builder.load_file('kv-files/dashboard_screen.kv')
        Builder.load_file('kv-files/setup_screen.kv')

ForestApp().run()