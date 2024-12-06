from kivy.clock import Clock


class Timer:
    def __init__(self, app_instance):
        self.work_minutes = 25
        self.break_minutes = 5

        self.timer_seconds = self.work_minutes * 60
        self.timer_period = 'work'
        self.tick_event = None

        self.app_instance = app_instance
        self.time = 0

    def start_timer(self):
        if self.tick_event is None:
            self.tick_event = Clock.schedule_interval(self.count_down, 1)
            self.time += 1
            

    def count_down(self, dt):
        if self.time == 20:
            self.app_instance.update_user_session_data()
            self.time = 0

        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            minutes, seconds = divmod(self.timer_seconds, 60)
            self.app_instance.get_timer_label().text = f"{minutes:02}:{seconds:02}"
        else:
            self.shift_period()

    def stop_timer(self):
        if self.tick_event:
            self.tick_event.cancel()
            self.tick_event = None

    def shift_period(self):
        if self.timer_period == 'work':
            self.timer_period = 'break'
            self.timer_seconds = self.break_minutes * 60
            self.app_instance.get_timer_label().text = f"{self.break_minutes}:00"
        elif self.timer_period == 'break':
            self.timer_period = 'work'
            self.timer_seconds = self.work_minutes * 60
            self.app_instance.get_timer_label().text = f"{self.work_minutes}:00"

        self.start_timer()

    def default_timer_settings(self):
        self.stop_timer()

        self.work_minutes = 25
        self.break_minutes = 5

        self.timer_seconds = self.work_minutes * 60
        self.timer_period = 'work'
        self.tick_event = None
        self.time = 0

        self.app_instance.root.get_screen(
            'dashboard').ids.timer_label.text = f'0{self.work_minutes}:00' if self.work_minutes < 10 else f'{self.work_minutes}:00'
        self.app_instance.root.get_screen(
            'setup').ids.timer_preview.text = f'0{self.work_minutes}:00' if self.work_minutes < 10 else f'{self.work_minutes}:00'

    def sync_timer_changes(self):

        self.app_instance.root.get_screen(
            'dashboard').ids.timer_label.text = f'0{self.work_minutes}:00' if self.work_minutes < 10 else f'{self.work_minutes}:00'
        self.app_instance.root.get_screen(
            'setup').ids.timer_preview.text = f'0{self.work_minutes}:00' if self.work_minutes < 10 else f'{self.work_minutes}:00'

        self.app_instance.settings_dialog.dismiss()
        self.app_instance.show_success_dialog()

    def set_timer_settings(self, work_time, break_time):
        self.stop_timer()

        self.work_minutes = work_time
        self.break_minutes = break_time
        self.timer_seconds = self.work_minutes * 60

        self.timer_period = 'work'
        self.tick_event = None

        self.sync_timer_changes()
