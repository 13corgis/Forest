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

ForestApp().run()