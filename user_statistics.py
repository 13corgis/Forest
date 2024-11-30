import pandas as pd
import altair as alt


class UserStatistics:
    def __init__(self, instance):
        self.app_instance = instance

        self.user_data = None

    # ! Encapsulated Common Calls
    def update_user_stats(self):
        self.app_instance.root.get_screen('dashboard').ids.loading_stats.active = True

        self.fetch_data()
        self.create_bar_chart()
        self.create_pie_chart()

    # ! Update the Components in the Statistics Screen to Display the Updated Charts
    def display_user_stats(self):
        self.app_instance.root.get_screen('dashboard').ids.loading_stats.active = False

        self.app_instance.root.get_screen('statistics').ids.chart_1.source = "resources/pie_chart.png"

        self.app_instance.root.get_screen('statistics').ids.chart_2.source = "resources/bar_chart.png"

        self.app_instance.root.current = 'statistics'

        self.app_instance.root.get_screen('statistics').ids.charts.swipe_left()

    # ! Bar Chart of the work spent per day in hours over the last 7 sessions (in orange) +
    # ! Mean of work spent per day over the last 7 sessions (in red)
    def create_bar_chart(self):

        bar = alt.Chart(self.user_data.tail(7)).mark_bar(color='orange').encode(
            x='date:N',
            y='work_per_day:Q'
        )

        rule = alt.Chart(self.user_data.tail(7)).mark_rule(color='red').encode(
            y='mean(work_per_day):Q'
        )

        (bar + rule).properties(width=600, title='Average Hours Spent Working over the Last 7 Sessions',
                                background='transparent').save("resources/bar_chart.png")

    # ! Pie Chart of the Latest Piece of Data (Last Session / Date Logged)
    def create_pie_chart(self):
        latest_data = pd.DataFrame(
            {
                'legend': ['Work Spent Today', 'Break Spent Today'],
                'data': [f"{self.user_data['work_per_day'].iloc[-1]: .02}", f"{self.user_data['break_per_day'].iloc[-1]: .02}"]
            }
        )

        base = alt.Chart(latest_data).encode(
            alt.Theta("data:Q").stack(True),
            alt.Color("legend:N").legend()
        )

        pie = base.mark_arc(outerRadius=120)
        text = base.mark_text(radius=140, size=18).encode(text="data:Q")

        (pie + text).properties(title=f'Time Invested in Hours ({self.user_data['date'].iloc[-1]})',
                                background='transparent').save(
            'resources/pie_chart.png')

    # ! Fetch the Latest User Data from the Database
    def fetch_data(self):
        # ! List of session_id (A day in this format is 1 session and is unique on a per-day basis: YEAR-MM-DAY)
        user_session_id_data = [
            (data['session_id']) for data in self.app_instance.collection.find_one(
                {'user_id': self.app_instance.current_user}, {'sessions.session_id': 1, '_id': 0})['sessions']]

        # ! List of total_work_time per day (parsed as hours instead of seconds)
        user_work_time_data = [
            (data['total_work_time'] / 3600) for data in self.app_instance.collection.find_one(
                {'user_id': self.app_instance.current_user}, {'sessions.total_work_time': 1, '_id': 0})['sessions']]

        # ! List of total_breaK_time per day (parsed as hours instead of seconds)
        user_break_time_data = [
            (data['total_break_time'] / 3600) for data in self.app_instance.collection.find_one(
                {'user_id': self.app_instance.current_user}, {'sessions.total_break_time': 1, '_id': 0})['sessions']]

        self.user_data = pd.DataFrame({
            'date': user_session_id_data,
            'work_per_day': user_work_time_data,
            'break_per_day': user_break_time_data
        })

