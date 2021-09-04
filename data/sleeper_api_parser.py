import requests
from datetime import datetime
from utils import convert_time
from lxml import html
import os
import debug
import json

API_URL = "https://api.sleeper.app/v1/league/"

class SleeperFantasyInfo():
    def __init__(self, league_id, user_id, week):
        self.league_id = league_id
        self.user_id = user_id
        self.week = week
        self.teams_info = self.get_teams(self.league_id)
        self.roster_id = self.get_roster_id(self.teams_info, self.user_id)
        self.matchup = self.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)

    def refresh_matchup(self):
        self.matchup = self.get_matchup(self.roster_id, self.league_id, self.week, self.teams_info)
        return self.get_matchup_points(self.matchup, self.league_id)

    def refresh_scores(self):
        return self.get_matchup_points(self.matchup, self.league_id)

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
                        matchup_info['user_av'] = next((item for item in teams if item['roster_id'] == team_roster_id))['avatar']
                        matchup_info['user_name'] = next((item for item in teams if item['roster_id'] == team_roster_id))['name']
                        matchup_info['user_team'] = next((item for item in teams if item['roster_id'] == team_roster_id))['team']
                for matchup in matchups:
                    if matchup['matchup_id'] == matchup_id and matchup['roster_id'] != team_roster_id:
                        matchup_info['opp_roster_id'] = matchup['roster_id']
                        matchup_info['opp_av'] = next((item for item in teams if item['roster_id'] == matchup['roster_id']))['avatar']
                        matchup_info['opp_name'] = next((item for item in teams if item['roster_id'] == matchup['roster_id']))['name']
                        matchup_info['opp_team'] = next((item for item in teams if item['roster_id'] == matchup['roster_id']))['team']
            return matchup_info
        except requests.exceptions.RequestException as e:
            print("Error encountered, Can't reach Sleeper API", e)
            return matchup_info
        except IndexError:
            print("uh oh")
            return matchup_info
        except Exception as e:
            print("something bad?", e)

    def get_matchup_points(self, matchup, league_id):
        # sleeper unfortunately changed the best way for me to do this
        # so now this is the work-around until a better solution presents itself
        print('checking scores btw')
        try:
            user_url = 'https://sleeper.app/roster/{0}/{1}'.format(league_id, matchup['user_roster_id'])
            opp_url = 'https://sleeper.app/roster/{0}/{1}'.format(league_id, matchup['opp_roster_id'])
            user_info = requests.get(user_url)
            opp_info = requests.get(opp_url)
            matchup['user_score'] = self.parse_score(user_info)
            matchup['opp_score'] = self.parse_score(opp_info)
            return matchup
        except requests.exceptions.RequestException as e:
            print("Error encountered, Can't reach Sleeper API", e)
            return matchup_info
        except IndexError:
            print("index error ", e)
            return matchup_info
        except Exception as e:
            print("general exception ", e)

    def parse_score(self, user_info):
        score = 0.0
        tree = html.fromstring(user_info.content)
        # oh fuck yeah bud let's duct tape the shit out of this
        for p in tree.xpath("//div[@class='players']//div[contains(@class, 'real ')]/text()"):
            try:
                fp = float(p)
                score += fp
            # this catches the '-' scores
            except:
                pass
        return score

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
                user_dict = {"name": name, "id": user_id, "avatar": avatar, "team": team_name}
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

def get_draft(league_id):
    """
        get draft infoooo0o0o0o0o
    """
    debug.info('getting draft')
    url = '{0}{1}/drafts'.format(API_URL, league_id)
    try:
        get_player_list()
        drafts = requests.get(url)
        drafts = drafts.json()
        # this should obv be variable but it'll change once per year so
        draft = [d for d in drafts if d['season'] == '2022']
        return draft[0]
    except requests.exceptions.RequestException as e:
        print("Error encountered, Can't reach Sleeper API", e)
        return drafts
    except IndexError:
        print("Index Error", e)
        return drafts
    except Exception as e:
        print("General Exception", e)

    def get_roster_id(self, teams, user_id):
        user = next((item for item in teams if item['id'] == user_id))
        return user['roster_id']

    def get_avatars(self, teams):
        debug.info('getting avatars')
        logospath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logos'))
        if not os.path.exists(logospath):
            os.makedirs(logospath, 0777)
        for team in teams:
            avatar = team['avatar']
            filename = os.path.join(logospath, '{0}.png'.format(team['display_name']))
            if not os.path.exists(filename):
                debug.info('downloading avatar for {0}'.format(team['display_name']))
                av_url = 'https://sleepercdn.com/avatars/thumbs/{0}'.format(avatar)
                r = requests.get(av_url, stream=True)
                with open(filename, 'wb') as fd:
                    print(filename)
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)

    # def get_player_list(self):
    #     debug.info('getting list of players')
    #     playerspath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    #     big_players = os.path.join(playerspath, 'players_big.json')
    #     reduced_players = os.path.join(playerspath, 'players.json')
    #     # doing this while I figure out how I want to handle it, and to make sure I don't blow anything up
    #     if 1 == 0:
    #         if not os.path.exists(big_players):
    #             debug.info('downloading players')
    #             p_url = 'https://api.sleeper.app/v1/players/nfl'
    #             r = requests.get(p_url, stream=True)
    #             with open(big_players, 'wb') as fd:
    #                 for chunk in r.iter_content(chunk_size=128):
    #                     fd.write(chunk)
    #         if not os.path.exists(reduced_players):
    #             debug.info('getting shreddy bro')
    #             playerdict = json.load(open(big_players))
    #             reduceddict = {d['player_id']:d['position'] for d in playerdict.values()}
    #             with open(reduced_players, 'wb') as fd:
    #                 fd.write(json.dumps(reduceddict))
