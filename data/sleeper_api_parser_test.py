from pprint import pprint
import requests
from datetime import datetime
from utils import convert_time
from unittest import mock
import os
import debug
import json

API_URL = "https://api.sleeper.app/v1/league/"

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == '0':
        with open('test_data/matchup_1_start.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)
    elif args[0] == '1':
        with open('test_data/matchup_1_play_1.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)
    elif args[0] == '2':
        with open('test_data/matchup_1_play_2.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)
    elif args[0] == '3':
        with open('test_data/matchup_1_play_3.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)
    elif args[0] == '4':
        with open('test_data/matchup_1_play_4.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)
    elif args[0] == '5':
        with open('test_data/matchup_1_final.json') as f:
            j = json.load(f)
        return MockResponse(j, 200)

    return MockResponse(None, 404)

class SleeperFantasyInfo():
    def __init__(self, league_id, user_id, week):
        self.league_id = league_id
        self.user_id = user_id
        self.week = week
        self.teams_info = self.get_teams(self.league_id)
        self.roster_id = self.get_roster_id(self.teams_info, self.user_id)
        self.matchup = self.get_matchup(
            self.roster_id, self.league_id, self.week, self.teams_info)

    def refresh_matchup(self):
        self.matchup = self.get_matchup(
            self.roster_id, self.league_id, self.week, self.teams_info)
        return self.get_points(self.matchup)

    def refresh_scores(self):
        return self.get_points(self.matchup)

    def get_matchup(self, team_roster_id, league_id, week, teams):
        """
            get all matchups this week and find the matchup you care about
        """
        # this is for pre-game of week 1
        if week == 0:
            week = 1
        url = '{0}{1}/matchups/{2}'.format(API_URL, league_id, week)
        matchup_id = 0
        matchup_info = {}
        try:
            matchups = requests.get(url)
            matchups = matchups.json()
            for matchup in matchups:
                if matchup['roster_id'] == team_roster_id:
                    matchup_id = matchup['matchup_id']
                    matchup_info['matchup_id'] = matchup['matchup_id']
                    matchup_info['user_roster_id'] = team_roster_id
                    matchup_info['user_av'] = next(
                        (item for item in teams if item['roster_id'] == team_roster_id))['name']
                    matchup_info['user_name'] = next(
                        (item for item in teams if item['roster_id'] == team_roster_id))['name']
                    matchup_info['user_team'] = next(
                        (item for item in teams if item['roster_id'] == team_roster_id))['team']
                for matchup in matchups:
                    if matchup['matchup_id'] == matchup_id and matchup['roster_id'] != team_roster_id:
                        matchup_info['opp_roster_id'] = matchup['roster_id']
                        matchup_info['opp_av'] = next(
                            (item for item in teams if item['roster_id'] == matchup['roster_id']))['name']
                        matchup_info['opp_name'] = next(
                            (item for item in teams if item['roster_id'] == matchup['roster_id']))['name']
                        matchup_info['opp_team'] = next(
                            (item for item in teams if item['roster_id'] == matchup['roster_id']))['team']
            return matchup_info
        except requests.exceptions.RequestException as e:
            print("Error encountered, Can't reach Sleeper API", e)
            return matchup_info
        except IndexError:
            print("uh oh")
            return matchup_info
        except Exception as e:
            print("something bad?", e)

    def get_test_scores(self, n):
        """
            get all matchups this week and find the matchup you care about
        """
        j = {}
        if n == 0:
            with open('test_data/matchup_1_start.json') as f:
                j = json.load(f)
        elif n == 1:
            with open('test_data/matchup_1_play_1.json') as f:
                j = json.load(f)
        elif n == 2:
            with open('test_data/matchup_1_play_2.json') as f:
                j = json.load(f)
        elif n == 3:
            with open('test_data/matchup_1_play_3.json') as f:
                j = json.load(f)
        elif n == 4:
            with open('test_data/matchup_1_play_4.json') as f:
                j = json.load(f)
        elif n == 5:
            with open('test_data/matchup_1_final.json') as f:
                j = json.load(f)
        game = {}
        for matchup in j:
            if matchup['roster_id'] == 1:
                game['user_score'] = matchup['points']
            if matchup['roster_id'] != 1:
                game['opp_score'] = matchup['points']
        return game

    def get_points(self, game):
        debug.info('checking sleeper scores for game {}'.format(game))
        try:
            matchup_url = 'https://api.sleeper.app/v1/league/{0}/matchups/{1}'.format(
                self.league_id, self.week)
            matchups = requests.get(matchup_url)
            matchups = matchups.json()
            for matchup in matchups:
                if matchup['roster_id'] == game['user_roster_id']:
                    game['user_score'] = matchup['points']
                if matchup['roster_id'] == game['opp_roster_id']:
                    game['opp_score'] = matchup['points']
            return game
        except requests.exceptions.RequestException as e:
            print("Error encountered, Can't reach Sleeper API", e)
            return game
        except IndexError:
            print("index error ", e)
            return game
        except Exception as e:
            print("general exception ", e)

    def get_teams(self, league_id):
        debug.info('getting teams')
        users_url = '{0}{1}/users'.format(API_URL, league_id)
        rosters_url = '{0}{1}/rosters'.format(API_URL, league_id)
        user_info = []
        try:
            users = requests.get(users_url)
            users = users.json()
            self.get_avatars(users)
            for user in users:
                name = user['display_name']
                avatar = user['avatar']
                user_id = user['user_id']
                team_name = user['metadata'].get('team_name')
                user_dict = {"name": name, "id": user_id,
                             "avatar": avatar, "team": team_name}
                user_info.append(user_dict)
            rosters = requests.get(rosters_url)
            rosters = rosters.json()
            for roster in rosters:
                for user in user_info:
                    if user['id'] == roster['owner_id']:
                        user['roster_id'] = roster['roster_id']
                        user['players'] = roster['players']
                        break
            return user_info
        except requests.exceptions.RequestException:
            print("Error encountered, Can't reach Sleeper API")
            return 0
        except IndexError:
            print("something somehow ended up out of index")
            return 0

    def get_roster_id(self, teams, user_id):
        user = next((item for item in teams if item['id'] == user_id))
        return user['roster_id']

    def get_avatars(self, teams):
        debug.info('getting avatars')
        logospath = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'logos'))
        if not os.path.exists(logospath):
            os.makedirs(logospath, 0o777)
        for team in teams:
            avatar = team['avatar']
            filename = os.path.join(
                logospath, '{0}.png'.format(team['display_name']))
            if not os.path.exists(filename):
                debug.info('downloading avatar for {0}'.format(
                    team['display_name']))
                av_url = 'https://sleepercdn.com/avatars/thumbs/{0}'.format(
                    avatar)
                r = requests.get(av_url, stream=True)
                with open(filename, 'wb') as fd:
                    print(filename)
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
