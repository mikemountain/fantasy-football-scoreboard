from utils import get_file
import json
import os


class ScoreboardConfig:
    def __init__(self, filename_base, args):
        json = self.__get_config(filename_base)
        # Misc config options
        # self.opening_day = json["opening_day"]
        self.debug = json["debug"]
        self.platform = json["platform"]
        self.year = json["year"]

        self.sleeper_league_id = json["sleeper"]["league_id"]
        self.sleeper_user_id = json["sleeper"]["user_id"]

        self.yahoo_consumer_key = json["yahoo"]["consumer_key"]
        self.yahoo_consumer_secret = json["yahoo"]["consumer_secret"]
        self.yahoo_game_id = json["yahoo"]["game_id"]
        self.yahoo_league_id = json["yahoo"]["league_id"]
        self.yahoo_team_id = json["yahoo"]["team_id"]

        self.espn_s2 = json["espn"]["espn_s2"]
        self.espn_swid = json["espn"]["swid"]
        self.espn_team_id = json["espn"]["team_id"]
        self.espn_league_id = json["espn"]["league_id"]
        # self.user_id = json["user_id"]
        # self.league_id = json["league_id"]
        # config options from arguments. If the argument was passed, use it, else use the one from config file.
        # if args.user_id:
        #     print(args.user_id)
        #     self.user_id = args.user_id
        # if args.league_id:
        #     self.league_id = args.league_id
        #else:
        #    self.fav_team_id = json['fav_team_id']

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file(filename)
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)
        reference_config = self.read_json(filename)

        return reference_config
