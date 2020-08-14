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
        self.draft_needs_refresh = True
        # get team id
        self.user_id = self.config.user_id
        # get league id
        self.league_id = self.config.league_id
        # Get the opening day to calculate what week it is
        self.week = self.get_week()
        # draft status
        self.draft = sleeper.get_draft(self.league_id)
        self.draft_status = self.draft['status']
        self.draft_start = self.draft['start_time']
        self.refresh_start()
        # Fetch the teams info
        self.teams_info = sleeper.get_teams(self.config.league_id)
        self.roster_id = sleeper.get_roster_id(self.teams_info, self.user_id)
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)

    def get_week(self):
        # testing
        # return 5
        today = datetime.today()
        days_since_start = (today - datetime.strptime(self.config.opening_day, "%Y-%m-%d")).days
        week = int(math.floor((days_since_start / 7) + 1))
        return week

    def get_current_date(self):
        # testing
        # return datetime(2020, 9, 13, 18, 0, 0, 329908) # During
        # return datetime(2020, 9, 15, 18, 0, 0, 329908) # Final
        return datetime.utcnow()

    def refresh_matchup(self):
        self.matchup = sleeper.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)
        self.needs_refresh = False

    def refresh_draft(self):
        self.draft = sleeper.get_draft(self.league_id)
        self.draft_status = self.draft['status']
        self.draft_start = self.draft['start_time']
        self.draft_sleep = 43200
        if self.draft_start:
            draft_delta = datetime.fromtimestamp(self.draft_start/1000.0) - datetime.now()
            if draft_delta.days > 0:
                self.draft_dt = '{} DAYS'.format(draft_delta.days)
            elif (draft_delta.seconds / 3600) > 0:
                self.draft_dt = '{} HOURS'.format(draft_delta.seconds / 3600)
                self.draft_sleep = 3600
            elif (draft_delta.seconds / 60) > 0:
                if (draft_delta.seconds / 60) == 1:
                    self.draft_dt = '{} MINUTE'.format(draft_delta.seconds / 60)
                else:
                    self.draft_dt = '{} MINUTES'.format(draft_delta.seconds / 60)
                self.draft_sleep = 60
            else:
                self.draft_dt = '{} SECONDS'.format(draft_delta.seconds)
                self.draft_sleep = 0.1 # turbo mode let's go
        else:
            self.draft_dt = 'NOT SET'
        self.draft_needs_refresh = False

    def refresh_start(self):
        self.start_sleep = 43200
        start_delta = datetime.strptime(self.config.opening_day, "%Y-%m-%d") - datetime.now()
        if start_delta.days == 1:
            self.start_dt = '{} DAY'.format(start_delta.days + 1)
        else:
            self.start_dt = '{} DAYS'.format(start_delta.days + 1)