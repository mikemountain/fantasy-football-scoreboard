import requests
from datetime import datetime
from utils import convert_time
import os
import debug
import json
from yahoo_oauth import OAuth2

# https://fantasysports.yahooapis.com/fantasy/v2/games;game_codes=nfl I'm almost positive this is how to find the game id (406) but I totally forget now

class YahooFantasyInfo():
    def __init__(self, yahoo_consumer_key, yahoo_consumer_secret, game_id, league_id, week):
        self.league_id = league_id
        self.game_id = game_id
        self.week = week
        self.auth_info = {"consumer_key": yahoo_consumer_key, "consumer_secret": yahoo_consumer_secret}

        # load or create OAuth2 refresh token
        token_file_path = os.path.join("../auth", "token.json")
        if os.path.isfile(token_file_path):
            with open(token_file_path) as yahoo_oauth_token:
                auth_info = json.load(yahoo_oauth_token)
        else:
            with open(token_file_path, "w") as yahoo_oauth_token:
                json.dump(auth_info, yahoo_oauth_token)

        if "access_token" in auth_info.keys():
            self._yahoo_access_token = auth_info["access_token"]

        # complete OAuth2 3-legged handshake by either refreshing existing token or requesting account access
        # and returning a verification code to input to the command line prompt
        self.oauth = OAuth2(None, None, from_file=token_file_path)
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()

        self.matchup = self.get_matchup(self.game_id, self.league_id, week)
    
    def get_matchup(self, game_id, league_id, week):
        self.refresh_access_token()
        url = "https://fantasysports.yahooapis.com/fantasy/v2/league/{0}.l.{1};out=scoreboard;week={2}".format(self.game_id, self.league_id, week)
        response = self.oauth.session.get(url, params={'format': 'json'})
        matchup = response.json()["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]["0"]["matchup"]["0"]["teams"]
        matchup_info = {}
        for team in matchup:
            if not isinstance(matchup[team], int):
                if matchup[team]['team'][0][3]:
                    matchup_info['user_name'] = matchup[team]['team'][0][19]['managers'][0]['manager']['nickname']
                    matchup_info['user_av'] = matchup[team]['team'][0][19]['managers'][0]['manager']['image_url']
                    matchup_info['user_team'] = matchup[team]['team'][0][2]['name']
                    matchup_info['user_proj'] = matchup[team]['team'][1]['team_projected_points']['total']
                    matchup_info['user_score'] = matchup[team]['team'][1]['team_points']['total']
                else:
                    matchup_info['opp_name'] = matchup[team]['team'][0][19]['managers'][0]['manager']['nickname']
                    matchup_info['opp_av'] = matchup[team]['team'][0][19]['managers'][0]['manager']['image_url']
                    matchup_info['opp_team'] = matchup[team]['team'][0][2]['name']
                    matchup_info['opp_proj'] = matchup[team]['team'][1]['team_projected_points']['total']
                    matchup_info['opp_score'] = matchup

    def get_avatars(self, teams):
        self.refresh_access_token()
        debug.info('getting avatars')
        logospath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logos'))
        if not os.path.exists(logospath):
            os.makedirs(logospath, 0777)
        filename = os.path.join(logospath, '{0}.png'.format(teams['user_name']))
        if not os.path.exists(filename):
            debug.info('downloading avatar for {0}'.format(teams['user_name']))
            r = requests.get(teams['user_av'], stream=True)
            with open(filename, 'wb') as fd:
                print(filename)
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
        filename = os.path.join(logospath, '{0}.png'.format(teams['opp_name']))
        if not os.path.exists(filename):
            debug.info('downloading avatar for {0}'.format(teams['opp_name']))
            r = requests.get(teams['opp_av'], stream=True)
            with open(filename, 'wb') as fd:
                print(filename)
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)

    def refresh_access_token(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
