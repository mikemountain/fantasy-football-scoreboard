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
        self.draft_needs_refresh = False
        self.check_scores = True
        # get team id
        self.user_id = self.config.user_id
        # get league id
        self.league_id = self.config.league_id
        # Get the opening day to calculate what week it is
        self.week = self.get_week()
        # draft status
        # self.draft = sleeper.get_draft(self.league_id)
        # self.draft_status = self.draft['status']
        # self.draft_start = self.draft['start_time']
        # self.refresh_start()
        # Fetch the teams info
        self.teams_info = sleeper.get_teams(self.config.league_id)
        self.roster_id = sleeper.get_roster_id(self.teams_info, self.user_id)
        # self.my_players = self.get_players()
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)

    def get_week(self):
        today = datetime.today()
        days_since_start = (today - datetime.strptime(self.config.opening_day, "%Y-%m-%d")).days
        week = int(math.floor((days_since_start / 7) + 1))
        return week

    def get_current_date(self):
        # pretty dumb function but I use this to test in off season
        return datetime.utcnow()

    def refresh_matchup(self):
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)
        self.matchup = sleeper.get_matchup_points(self.matchup, self.league_id)
        self.needs_refresh = False

    # this looks rough
    def refresh_scores(self):
        self.matchup = sleeper.get_matchup_points(self.matchup, self.league_id)
        self.needs_refresh = False

    def refresh_rosters(self):
        self.teams_info = sleeper.get_teams(self.config.league_id)

    def get_players(self):
        user = next((item for item in self.teams_info if item['id'] == self.user_id))
        return user['players']

    def refresh_draft(self):
        self.draft = sleeper.get_draft(self.league_id)
        self.draft_status = self.draft['status']
        self.draft_start = self.draft['start_time']
        self.draft_sleep = 43200
        if self.draft_start:
            draft_delta = datetime.fromtimestamp(self.draft_start/1000.0) - datetime.now()
            self.draft_dt = self.set_dt(draft_delta)
        else:
            self.draft_dt = 'NOT SET'
        self.draft_needs_refresh = False

    # def refresh_start(self):
    #     self.sleep = 43200
    #     start_delta = datetime.strptime("{} 20:20:00 EDT".format(self.config.opening_day), "%Y-%m-%d %H:%M:%S %Z") - datetime.now()
    #     self.start_dt = self.set_dt(start_delta)

    def set_dt(self, old_dt):
        if old_dt.days == 1:
            new_dt = '{} DAY'.format(old_dt.days)
        elif old_dt.days > 0:
            new_dt = '{} DAYS'.format(old_dt.days)
        elif (old_dt.seconds / 3600) > 0:
            new_dt = '{} HOURS'.format(old_dt.seconds / 3600)
            self.sleep = 3600
        elif (old_dt.seconds / 60) > 0:
            if (old_dt.seconds / 60) == 1:
                new_dt = '{} MINUTE'.format(old_dt.seconds / 60)
            else:
                new_dt = '{} MINUTES'.format(old_dt.seconds / 60)
            self.sleep = 60
        else:
            new_dt = '{} SECONDS'.format(old_dt.seconds)
            self.sleep = 0.1 # turbo mode let's go
        return new_dt

    def check_if_playing(self):
        time = self.get_current_date()
        # thursday, sunday, monday
        # I gotta find a better way to do this but I ain't doin' it now
        if (time.weekday() == 4 and time.hour >= 0 and time.hour <= 4) or ((time.weekday() == 6 and time.hour >= 13) or (time.weekday() == 0 and time.hour <= 4)) or ((time.weekday() == 0 and time.hour >= 19) or (time.weekday() == 1 and time.hour <= 4)):
            self.check_scores = True
        else:
            self.check_scores = False