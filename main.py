from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import FadeTransition
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.dialog import *
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from screeninfo import get_monitors
from pymongo import MongoClient
from datetime import datetime
from pomodoro_timer import Timer
from user_statistics import UserStatistics


# ! Initialize Window - - - - - - - - - - - -
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


class ForestApp(MDApp):
    def __init__(self, **kwargs):
        super(ForestApp, self).__init__(**kwargs)
        # ! Database Connector - - - - - - - - - - - -
        try:
            self._uri = "mongodb+srv://treeInForest:IAmATree@forest.htdun.mongodb.net/?retryWrites=true&w=majority&appName=Forest"
            self._client = MongoClient(self._uri)
            self._database = self._client["test"]
            self._collection = self._database["users"]

            self.date_today = datetime.today().strftime("%Y-%m-%d")
        except Exception as e:
            raise Exception(
                "The following error occurred: ", e)

        self.current_user = None

        # Timer
        self.timer = Timer(self)

        # Statistics
        self.user_statistics = None

        # Member Variables - Background
        self.selected_bg = 0

        # Member Variables - Menu Components
        self.menu = None
        self.settings_dialog = None
        self.help_dialog = None

    def build(self):
        self.init_bg_images()
        init_window()
        Window.hide()

        self.load_kv_files()

        return Builder.load_file('kv-files/forest.kv')

    def on_start(self):
        # ! Initializations - - - - - - - - - - - -
        self.init_settings_dialog()
        self.init_help_dialog()
        self.init_profile_menu()

        Window.show()

        Clock.schedule_once(lambda dt: self.enter_app(), 5)

    # ! Update User Session Data per Timer Tick - - - - - - - - - - - -
    def update_user_session_data(self):

        if self._collection.find_one({'user_id': self.current_user, 'sessions.session_id': self.date_today}) is None:
            # ! Log today as a session
            self._collection.update_one({'user_id': self.current_user}, {
                '$push': {'sessions': {'session_id': self.date_today, 'total_work_time': 0, 'total_break_time': 0}}})
        else:
            # ! There is an existing session for today
            # ! So update total work time
            if self.timer.timer_period == 'work':
                self._collection.update_one({'user_id': self.current_user, 'sessions.session_id': self.date_today},
                                            {'$inc': {'sessions.$.total_work_time': 20}})
            # ! Break period
            elif self.timer.timer_period == 'break':
                self._collection.update_one({'user_id': self.current_user, 'sessions.session_id': self.date_today},
                                            {'$inc': {'sessions.$.total_break_time': 20}})

    # ! Login Attempt - - - - - - - - - - - -
    def attempt_login(self):
        login_textfield_input = self.root.get_screen('login').ids.login_textfield.text
        login_passfield_input = self.root.get_screen('login').ids.login_passfield.text

        if self._collection.find_one({'user_id': login_textfield_input, 'password': login_passfield_input}) is not None:

            self.show_success_dialog()

            self.current_user = login_textfield_input

            self.user_statistics = UserStatistics(self)

            self.update_user_session_data()

            self.root.current = 'dashboard'
        else:
            MDDialog(MDDialogIcon(icon='alert-circle'),
                     MDDialogHeadlineText(text='Invalid Credentials'),
                     MDDialogSupportingText(
                         text='Re-enter your details or create an account if you\'re new here.')).open()

    # ! Signup Attempt - - - - - - - - - - - -
    def attempt_signup(self):
        signup_textfield_input = self.root.get_screen('login').ids.signup_textfield.text
        signup_passfield_input = self.root.get_screen('login').ids.signup_passfield.text
        signup_cfpassfield_input = self.root.get_screen('login').ids.signup_cfpassfield.text

        if self._collection.find_one({'user_id': signup_textfield_input}) is not None:
            MDDialog(MDDialogIcon(icon='account-check'),
                     MDDialogHeadlineText(text='User ID Taken'),
                     MDDialogSupportingText(
                         text='An account with the same User ID already exists. Please try a different User ID.')).open()
        else:
            if len(signup_textfield_input) >= 3 and len(signup_passfield_input) >= 3:
                if signup_passfield_input == signup_cfpassfield_input:
                    self._collection.insert_one(
                        {'user_id': signup_textfield_input, 'password': signup_passfield_input, 'sessions': []})

                    self.show_success_dialog()
                else:
                    MDDialog(MDDialogIcon(icon='alert-circle'),
                             MDDialogHeadlineText(text='Mismatched Passwords'),
                             MDDialogSupportingText(
                                 text='Double-check for typos to ensure passwords are identical.')).open()
            else:
                if len(signup_textfield_input) < 3:
                    MDDialog(MDDialogIcon(icon='alert-circle'),
                             MDDialogHeadlineText(text='Invalid User ID'),
                             MDDialogSupportingText(
                                 text='User ID must be at least 3 characters long.')).open()
                if len(signup_passfield_input) < 3:
                    MDDialog(MDDialogIcon(icon='alert-circle'),
                             MDDialogHeadlineText(text='Invalid Password'),
                             MDDialogSupportingText(
                                 text='Password must be at least 3 characters long.')).open()

    # ! Startup Sequence - - - - - - - - - - - -
    def enter_app(self):
        self.root.transition = FadeTransition(duration=1)
        self.root.current = 'startup'
        self.root.get_screen('startup').ids.intro.state = 'play'
        self.root.transition = FadeTransition(duration=0.3)
        Clock.schedule_once(lambda dt: self.to_login(), 6)

    def to_login(self):
        self.root.current = 'login'

    # ! Profile menu > logout - - - - - - - - - - - -
    def logout(self):
        self.timer.default_timer_settings()

        self.root.transition = FadeTransition(duration=0.15)

        self.root.get_screen('login').ids.login_passfield.text = ''
        self.root.current = 'login'
        self.menu.dismiss()

        self.root.transition = FadeTransition(duration=0.3)

    # ! Profile Menu - - - - - - - - - - - -
    def open_profile_menu(self):
        self.menu.open()

    # ! Success Dialog Sequence - - - - - - - - - - - -
    def show_success_dialog(self):
        success_dialog = MDDialog(MDDialogIcon(icon='check-circle', role='large'), theme_bg_color='Custom',
                                  md_bg_color=(0, 0, 0, 0))
        success_dialog.open()

        Clock.schedule_once(lambda dt: success_dialog.dismiss(), 2.5)

    # ! Change Dashboard Opacity on Dialog.open() and Dialog.dismiss() - - - - - - - - - - - -
    def change_opacity(self):
        components = [
            self.root.get_screen('dashboard').ids.timer_label,
            self.root.get_screen('dashboard').ids.dash_btns
        ]

        for comp in components:
            if comp.opacity == 1 or comp.opacity == 0.6:
                comp.opacity = 0
            elif comp.opacity == 0:
                if comp == components[0]:
                    comp.opacity = 1
                else:
                    comp.opacity = 0.6

    # ! Selected Background Tracker - - - - - - - - - - - -
    def manage_background(self, action, bg_paths=None):

        if bg_paths is None:
            bg_paths = ['resources/setup_0.mp4',
                        'resources/setup_1.mp4',
                        'resources/setup_2.mp4',
                        'resources/setup_3.mp4',
                        'resources/setup_4.mp4',
                        'resources/setup_5.mp4',
                        'resources/setup_6.mp4']

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

        self.root.get_screen('setup').ids.setup_bg.source = bg_paths[self.selected_bg]

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

    # ! Initialize / Asynchronously Load Background Resources - - - - - - - - - - - -
    def init_bg_images(self):
        bg_paths = [
            'resources/setup_0.mp4',
            'resources/setup_1.mp4',
            'resources/setup_2.mp4',
            'resources/setup_3.mp4',
            'resources/setup_4.mp4',
            'resources/setup_5.mp4',
            'resources/setup_6.mp4'
        ]

        image = AsyncImage(source='resources/setup_startup.mp4')

        for path in bg_paths:
            image = AsyncImage(source=path)

    # ! Load kv files - - - - - - - - - - - -
    def load_kv_files(self):
        Builder.load_file('kv-files/startup_screen.kv')
        Builder.load_file('kv-files/login_screen.kv')
        Builder.load_file('kv-files/dashboard_screen.kv')
        Builder.load_file('kv-files/setup_screen.kv')
        Builder.load_file('kv-files/statistics_screen.kv')

    # ! Get Timer Label - - - - - - - - - - - -
    def get_timer_label(self):
        return self.root.get_screen('dashboard').ids.timer_label


ForestApp().run()
