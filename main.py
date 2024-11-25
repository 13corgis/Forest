from kivymd.app import MDApp
from kivy.lang import Builder

class ForestApp(MDApp):
    def __init__(self, **kwargs):
        super(ForestApp, self).__init__(**kwargs)
        pass
    
    def build(self):
        self.load_kv_files()
        
        return Builder.load_file('kv-files/forest.kv')

    def on_start(self):
        pass
    
    def load_kv_files(self):
        Builder.load_file('kv-files/startup_screen.kv')
        Builder.load_file('kv-files/login_screen.kv')
        Builder.load_file('kv-files/dashboard_screen.kv')
        Builder.load_file('kv-files/setup_screen.kv')

ForestApp().run()