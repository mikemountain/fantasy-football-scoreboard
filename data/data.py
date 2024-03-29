from datetime import datetime, timezone
import math
import data.sleeper_api_parser as sleeper
import data.yahoo_api_parser as yahoo
import data.espn_api_parser as espn
import debug
import requests

API_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'


class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Get what week it is
        self.week = self.get_week()
        self.season_type = self.get_season_type()

        # which platform are we using
        self.platform = self.config.platform
        self.api = self.choose_api()

        # Flag to determine when to refresh data
        self.needs_refresh = True
        self.check_scores = True

        self.matchup = self.api.matchup

    def choose_api(self):
        debug.info(self.platform.lower())
        if self.platform.lower() == "sleeper":
            return sleeper.SleeperFantasyInfo(self.config.sleeper_league_id, self.config.sleeper_user_id, self.week)
        elif self.platform.lower() == "yahoo":
            return yahoo.YahooFantasyInfo(self.config.yahoo_consumer_key, self.config.yahoo_consumer_secret, self.config.yahoo_game_id, self.config.yahoo_league_id, self.config.yahoo_team_id, self.week)
        elif self.platform.lower() == "espn":
            return espn.ESPNFantasyInfo(self.config.espn_league_id, self.config.espn_team_id, self.config.espn_swid, self.config.espn_s2, self.week, self.config.season)
        else:
            # this will break but I'll robustify it later
            print('You need to set one of ESPN, Yahoo, or Sleeper in the config file')
            return 0

    def get_season_type(self):
        # this is for that gap on espn where it's after the end of preseason, but there are like 12 days before the season starts
        season_type = requests.get(API_URL).json()
        if season_type['season']['type'] == 2 and season_type['leagues'][0]['season']['type']['type'] != 2:
            return 'kickoff'
        else:
            return 'season'

    def get_week(self):
        week_info = requests.get(API_URL).json()
        return week_info['week']['number']

    def get_current_date(self):
        # pretty dumb function but whatever
        return datetime.now(timezone.utc)

    def refresh_matchup(self):
        self.matchup = self.api.refresh_matchup()
        self.needs_refresh = False

    # this looks rough
    def refresh_scores(self):
        self.matchup = self.api.refresh_scores()
        self.needs_refresh = False

    def refresh_rosters(self):
        self.teams_info = self.api.get_teams(self.config.league_id)

    def get_players(self):
        user = next(
            (item for item in self.teams_info if item['id'] == self.user_id))
        return user['players']

    def test_game(self, n):
        return self.api.get_test_scores(n)

    # def refresh_draft(self):
    #     self.draft = sleeper.get_draft(self.league_id)
    #     self.draft_status = self.draft['status']
    #     self.draft_start = self.draft['start_time']
    #     self.draft_sleep = 43200
    #     if self.draft_start:
    #         draft_delta = datetime.fromtimestamp(self.draft_start/1000.0) - datetime.now()
    #         self.draft_dt = self.set_dt(draft_delta)
    #     else:
    #         self.draft_dt = 'NOT SET'
    #     self.draft_needs_refresh = False

    def refresh_start(self):
        self.sleep = 43200
        start_delta = datetime.strptime("{} 20:20:00 EDT".format(
            self.config.opening_day), "%Y-%m-%d %H:%M:%S %Z") - datetime.now()
        self.start_dt = self.set_dt(start_delta)

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
            self.sleep = 0.1  # turbo mode let's go
        return new_dt

    def check_if_playing(self):
        time = self.get_current_date()
        # thursday, sunday, monday
        # I gotta find a better way to do this but I ain't doin' it now
        if (time.weekday() == 4 and time.hour >= 0 and time.hour <= 4) or ((time.weekday() == 6 and time.hour >= 13) or (time.weekday() == 0 and time.hour <= 4)) or ((time.weekday() == 0 and time.hour >= 19) or (time.weekday() == 1 and time.hour <= 4)):
            self.check_scores = True
        else:
            self.check_scores = False
