import requests
from datetime import datetime
from utils import convert_time
import os
from pprint import pprint
import json

API_URL = "https://lm-api.reads.fantasy.espn.com/apis/v3/games/ffl/seasons"


class ESPNFantasyInfo():
    def __init__(self, league_id, team_id, swid, espn_s2, week, year):
        self.league_id = league_id
        self.team_id = int(team_id)
        self.week = week
        self.year = year
        self.cookies = {'swid': swid, 'espn_s2': espn_s2}
        self.teams_info = self.get_teams()
        self.matchup = self.get_matchup()

    def refresh_matchup(self):
        self.matchup = self.get_matchup()
        return self.matchup

    def refresh_scores(self):
        self.matchup = self.get_matchup()
        return self.matchup

    def get_matchup(self):
        print('getting matchup')
        matchup_info = {}
        try:
            url = '{0}/{1}/segments/0/leagues/{2}'.format(
                API_URL, self.year, self.league_id)
            matchups = requests.get(url, cookies=self.cookies, params={"view": "mBoxscore"}).json()
            for matchup in matchups['schedule']:
                if int(matchup['matchupPeriodId']) != self.week:
                    continue
                if int(matchup['home']['teamId']) == self.team_id:
                    matchup_info['user_name'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['team']
                    matchup_info['user_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))[
                        'avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['user_team'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['owner']
                    if 'pointsByScoringPeriod' in matchup['home']:
                        matchup_info['user_score'] = float(matchup['home']['pointsByScoringPeriod'].get(str(self.week), 0))
                    else:
                        matchup_info['user_score'] = float(
                            matchup['home'].get('rosterForCurrentScoringPeriod', {}).get('appliedStatTotal', 0))
                    matchup_info['opp_name'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['team']
                    matchup_info['opp_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))[
                        'avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['opp_team'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['owner']
                    if 'pointsByScoringPeriod' in matchup['away']:
                        matchup_info['opp_score'] = float(matchup['away']['pointsByScoringPeriod'].get(str(self.week), 0))
                    else:
                        matchup_info['opp_score'] = float(
                            matchup['away'].get('rosterForCurrentScoringPeriod', {}).get('appliedStatTotal', 0))
                elif int(matchup['away']['teamId']) == self.team_id:
                    matchup_info['user_name'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['team']
                    matchup_info['user_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))[
                        'avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['user_team'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['away']['teamId']))['owner']
                    if 'pointsByScoringPeriod' in matchup['away']:
                        matchup_info['user_score'] = float(matchup['away']['pointsByScoringPeriod'].get(str(self.week), 0))
                    else:
                        matchup_info['user_score'] = float(
                            matchup['away'].get('rosterForCurrentScoringPeriod', {}).get('appliedStatTotal', 0))
                    matchup_info['opp_name'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['team']
                    matchup_info['opp_av'] = next((item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))[
                        'avatar'].split("/")[-1].replace('.svg', '.png')
                    matchup_info['opp_team'] = next(
                        (item for item in self.teams_info if item['team_id'] == matchup['home']['teamId']))['owner']
                    if 'pointsByScoringPeriod' in matchup['home']:
                        matchup_info['opp_score'] = float(matchup['home']['pointsByScoringPeriod'].get(str(self.week), 0))
                    else:
                        matchup_info['opp_score'] = float(
                            matchup['home'].get('rosterForCurrentScoringPeriod', {}).get('appliedStatTotal', 0))
            return matchup_info
        except requests.exceptions.RequestException as e:
            print("Error encountered. Can't reach ESPN API:", e)
            return matchup_info
        except IndexError:
            print("ESPN API Index Error in get_matchup")
            return matchup_info
        except Exception as e:
            print("ESPN API Error in get_matchup:", e)

    def get_teams(self):
    	print('getting teams')
    	user_info = []
    	try:
        	url = '{0}/{1}/segments/0/leagues/{2}'.format(API_URL, self.year, self.league_id)
        	users = requests.get(url, cookies=self.cookies, params={"view": "mTeam"}).json()
        	for user in users['teams']:
            		avatar = user.get('logo', 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/National_Football_League_logo.svg/800px-National_Football_League_logo.svg.png')
            		team_id = user['id']
            		abbrev = user['abbrev']
            		team_name = user.get('location', '') + ' ' + user.get('nickname', '')
            		owner = user.get('primaryOwner', 'Unknown Owner')
            		user_dict = {"abbrev": abbrev, "team_id": team_id, "owner": owner, "team": team_name, "avatar": avatar, "display_name": None}
            		user_info.append(user_dict)
        	for member in users.get('members', []):
            		for ui in user_info:
                		if ui.get('owner') == member.get('id'):
                    			ui['display_name'] = member.get('displayName', 'Unknown Display Name')
                    			break
        	self.get_avatars(user_info)
        	return user_info
    	except requests.exceptions.RequestException:
        	print("Error encountered. Can't reach ESPN API")
        	return []
    	except IndexError:
        	print("Something somehow ended up out of index")
        	return []

    def get_avatars(self, teams):
     logospath = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'logos'))
     if not os.path.exists(logospath):
        os.makedirs(logospath, 0o777)
     default_avatar_url = 'https://example.com/default_avatar.png'  # Replace with your default avatar URL
     for team in teams:
        avatar = team['avatar']
        filename = os.path.join(
            logospath, '{0}'.format(avatar.split("/")[-1]))
        if not os.path.exists(filename):
            filename = os.path.join(logospath, 'default_avatar.png')  # Replace with your default avatar file path
        print('Downloading avatar for {0}'.format(team['display_name']))
        r = requests.get(avatar, stream=True)
        with open(filename, 'wb') as fd:
            print(filename)
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
