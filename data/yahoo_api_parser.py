from __future__ import print_function
from builtins import next
from datetime import datetime
from utils import convert_time
from lxml import html
from yfpy import Data
from yfpy.models import Game, StatCategories, User, Scoreboard, Settings, Standings, League, Player, Team, TeamPoints, TeamStandings, Roster
from yfpy.query import YahooFantasySportsQuery
import requests
import os
import debug
import json
import logging
import pprint
import warnings

def load_data(consumer, secret):
    browser_callback=False
    auth_dir = "."
    game_key = "399"
    game_code = "nfl"
    season = "2020"
    league_id = 0
    yahoo_info = {}
    yahoo_data=Data(".")
    yahoo_query = YahooFantasySportsQuery(
        auth_dir,
        league_id,
        game_id=game_key,
        game_code=game_code,
        offline=False,
        all_output_as_json=False,
        consumer_key='dj0yJmk9TTlodmluMVowaU5qJmQ9WVdrOWJqbFFWMjVRWm04bWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTMx',
        consumer_secret='49be06eaacd19d52cfc8d5d6ae1fd8c3b46639a7',
        browser_callback=False)
    ut = yahoo_query.get_user_teams()
    user = next((item for item in ut if item['game'].season == "2020" and item['game'].name == "Football"))
    league_id = (user['game'].teams['team'].team_key).split('.')[2]
    yahoo_query = YahooFantasySportsQuery(
        auth_dir,
        league_id,
        game_id=game_key,
        game_code=game_code,
        offline=False,
        all_output_as_json=False,
        consumer_key='dj0yJmk9TTlodmluMVowaU5qJmQ9WVdrOWJqbFFWMjVRWm04bWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTMx',
        consumer_secret='49be06eaacd19d52cfc8d5d6ae1fd8c3b46639a7',
        browser_callback=False)
    yahoo_info['yq'] = yahoo_query
    yahoo_query['user'] = user
    yahoo_info['team_id'] = user['game'].teams['team'].team_id
    yahoo_info['league_id'] = league_id
    return yahoo_info

def get_matchup(yahoo_info, week):
    """
        get all matchups this week and find the matchup you care about
    """
    # this is for pre-game of week 1
    if week == 0:
        week = 1
    matchup_info = {}
    team_id = yahoo_info['team_id']
    matchups = yahoo_info['yq'].get_league_matchups_by_week(week)
    matchup_info['matchup'] = next((item['matchup'].teams for item in matchups if item['matchup'].teams[0]['team'].team_id == team_id or item['matchup'].teams[1]['team'].team_id == team_id))
    matchup_info['user_team'] = next((item['team'] for item in matchup if item['team'].team_id == team_id))
    matchup_info['user_score'] = matchup_info['user_team'].team_points.total
    matchup_info['user_id'] = team_id
    matchup_info['user_av'] = matchup_info['user_team'].team_logos['team_logo'].url
    matchup_info['opp_team'] = next((item['team'] for item in matchup if iteam['team'].team_id != team_id))
    matchup_info['opp_score'] = matchup_info['opp_team'].team_points.total
    matchup_info['opp_id'] = matchup_info['opp_team'].team_id
    matchup_info['opp_av'] = matchup_info['opp_team'].team_logos['team_logo'].url
    return matchup_info

def get_matchup_points(yahoo_info, matchup):
    print('checking scores btw')
    yq = yahoo_info['yq']
    matchup['user_score'] = yq.get_team_stats_by_week(matchup['team_id'])['team_points'].total
    matchup['opp_score'] = yq.get_team_stats_by_week(matchup['opp_id'])['team_points'].total
    return matchup

# def get_teams(league_id):
#     debug.info('getting teams')
#     users_url = '{0}{1}/users'.format(API_URL, league_id)
#     rosters_url = '{0}{1}/rosters'.format(API_URL, league_id)
#     user_info = []
#     try:
#         users = requests.get(users_url)
#         users = users.json()
#         get_avatars(users)
#         for user in users:
#             name = user['display_name']
#             avatar = user['avatar']
#             user_id = user['user_id']
#             team_name = user['metadata'].get('team_name')
#             user_dict = {"name": name, "id": user_id, "avatar": avatar, "team": team_name}
#             user_info.append(user_dict)
#         rosters = requests.get(rosters_url)
#         rosters = rosters.json()
#         for roster in rosters:
#             for user in user_info:
#                 if user['id'] == roster['owner_id']:
#                     user['roster_id'] = roster['roster_id']
#                     user['players'] = roster['players']
#                     break
#         return user_info
#     except requests.exceptions.RequestException:
#         print("Error encountered, Can't reach Sleeper API")
#         return 0
#     except IndexError:
#         print("something somehow ended up out of index")
#         return 0

# def get_roster_id(teams, user_id):
#     user = next((item for item in teams if item['id'] == user_id))
#     return user['roster_id']

def get_avatars(matchup_info):
    debug.info('getting avatars')
    logospath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logos'))
    if not os.path.exists(logospath):
        os.makedirs(logospath, 0o777)
    usr_filename = os.path.join(logospath, '{0}.png'.format(matchup_info['team_id']))
    if not os.path.exists(usr_filename):
        r = requests.get(matchup_info['user_av'], stream=True)
        with open(usr_filename, 'wb') as fd:
            print(usr_filename)
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    opp_filename = os.path.join(logospath, '{0}.png'.format(matchup_info['opp_id']))
    if not os.path.exists(opp_filename):
        r = requests.get(matchup_info['opp_av'], stream=True)
        with open(opp_filename, 'wb') as fd:
            print(opp_filename)
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)