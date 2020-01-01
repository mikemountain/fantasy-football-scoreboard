from datetime import datetime, timedelta
import math
import sleeper_api_parser as sleeper
import debug

class Data:
    def __init__(self, config):
        self.idex = 0
        # Save the parsed config
        self.config = config
        # Flag to determine when to refresh data
        self.needs_refresh = True
        # get team id
        self.user_id = self.config.user_id
        # get league id
        self.league_id = self.config.league_id
        # Get the opening day to calculate what week it is
        #self.week = self.get_week()
        self.week = 16
        # Fetch the teams info
        self.teams_info = sleeper.get_teams(self.config.league_id)
        self.roster_id = sleeper.get_roster_id(self.teams_info, self.user_id)
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)

    def get_week(self):
        today = datetime.today()
        days_since_start = (today - datetime.strptime(self.config.opening_day, "%Y-%m-%d")).days
        week = int(math.floor((days_since_start / 7) + 1))
        return week

    def get_current_date(self):
        return datetime.utcnow()

    def refresh_matchup(self):
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)
        self.needs_refresh = False
