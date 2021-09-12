import requests
from datetime import datetime
from utils import convert_time
import os
import debug
import json

API_URL = "https://fantasy.espn.com/apis/v3/games/ffl/seasons"

class ESPNFantasyInfo():
    def __init__(self, league_id, team_id, swid, espn_s2, week, year):
        self.league_id = league_id
        self.team_id = int(team_id)
        self.week = week
        self.year = year
        self.cookies = {'swid': swid, 'espn_s2': espn_s2}
        self.teams_info = self.get_teams()
        self.matchup = self.get_matchup()

    # yeah these two are stupid and useless functions but right now I'm panicking trying to get this to work
    def refresh_matchup(self):
        return self.get_matchup()

    def refresh_scores(self):
        return self.get_matchup()

    def get_matchup(self):
        """
            get all matchups this week and find the matchup you care about
        """
        url = '{0}/{1}/segments/0/leagues/{2}'.format(API_URL, self.year, self.league_id)
        matchup_id = 0
        matchup_info = {}
        if self.week == 0:
            self.week = 1
        try:
            matchups = requests.get(url, cookies = self.cookies, params = {"view": "mBoxscore"})
            matchups = matchups.json()
            for matchup in matchups['schedule']:
                if int(matchup['matchupPeriodId']) != self.week:
                    continue
                if int(matchup['home']['teamId']) == self.team_id:
                    matchup_info['user_name'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['team']
                    matchup_info['user_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['user_team'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['owner']
                    matchup_info['user_score'] = float(matchup['home']['rosterForMatchupPeriod']['appliedStatTotal'])
                    matchup_info['opp_name'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['team']
                    matchup_info['opp_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['opp_team'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['owner']
                    matchup_info['opp_score'] = float(matchup['away']['rosterForMatchupPeriod']['appliedStatTotal'])
                elif int(matchup['away']['teamId']) == self.team_id:
                    matchup_info['user_name'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['team']
                    matchup_info['user_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['user_team'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['owner']
                    matchup_info['user_score'] = float(matchup['away']['rosterForMatchupPeriod']['appliedStatTotal'])
                    matchup_info['opp_name'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['team']
                    matchup_info['opp_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['opp_team'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['owner']
                    matchup_info['opp_score'] = float(matchup['home']['rosterForMatchupPeriod']['appliedStatTotal'])      
            print(matchup_info)
            return matchup_info
        except requests.exceptions.RequestException as e:
            print("Error encountered, Can't reach ESPN API", e)
            return matchup_info
        except IndexError:
            print("uh oh")
            return matchup_info
        except Exception as e:
            print("something bad?", e)

    def get_teams(self):
        debug.info('getting teams')
        url = '{0}/{1}/segments/0/leagues/{2}'.format(API_URL, self.year, self.league_id)
        user_info = []
        try:
            users = requests.get(url, cookies = self.cookies, params = {"view": "mTeam"})
            users = users.json()
            for user in users['teams']:
                avatar = user['logo']
                team_id = user['id']
                abbrev = user['abbrev']
                team_name = user['location'] + ' ' + user['nickname']
                owner = user['primaryOwner']
                user_dict = {"abbrev": abbrev, "team_id": team_id, "owner": owner, "team": team_name, "avatar": avatar}
                user_info.append(user_dict)
            for member in users['members']:
                for ui in user_info:
                    if ui['owner'] == member['id']:
                        ui['display_name'] = member['displayName']
                        break
            self.get_avatars(user_info)
            return user_info
        except requests.exceptions.RequestException:
            print("Error encountered, Can't reach Sleeper API")
            return 0
        except IndexError:
            print("something somehow ended up out of index")
            return 0

    def get_avatars(self, teams):
        debug.info('getting avatars')
        logospath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logos'))
        if not os.path.exists(logospath):
            os.makedirs(logospath, 0777)
        for team in teams:
            avatar = team['avatar']
            filename = os.path.join(logospath, '{0}'.format(avatar.split("/")[-1]))
            if not os.path.exists(filename):
                debug.info('downloading avatar for {0}'.format(team['display_name']))
                r = requests.get(avatar, stream=True)
                with open(filename, 'wb') as fd:
                    print(filename)
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                # can't render SVGs
                if filename.endswith('.svg'):
                    debug.warning('Warning! There are multiple SVG files that need to be converted manually into PNG due to crappy pi/python2 limitations. Check the ESPN SETUP STUFF part of the readme!')