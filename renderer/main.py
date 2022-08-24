from PIL import Image, ImageFont, ImageDraw, ImageSequence
# try:
#     from rgbmatrix import graphics
# except ImportError:
#     from RGBMatrixEmulator import graphics

from RGBMatrixEmulator import RGBMatrix
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
import time as t
import debug
import math

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        self.avsize = 19
        # use this to check if week has changed
        self.week = data.week
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)
        self.font_vs = ImageFont.truetype("fonts/CG pixel 3x5.ttf", 10)
        self.font_res = ImageFont.truetype("fonts/CG pixel 3x5.ttf", 6)

    def render(self):
        while True:
            if self.week > 0 and self.week < 19:
                debug.info('render game')
                self.__render_game()
            # weeks 17+, off season
            else:
                debug.info('Off season state')
                self.__render_off_season()

    def __render_game(self):
        debug.info('ping render_game')
        time = self.data.get_current_date()
        debug.info(time)
        # check if thursday and before 23h00 UTC
        if time.weekday() == 3 and time.hour <= 23 and time.minute <= 59:
            debug.info('Scheduled State, waiting 15 min')
            self._draw_pregame()
            t.sleep(900)
        # friday before 00h15 UTC
        elif time.weekday() == 4 and time.hour == 0 and time.minute <= 15:
            debug.info('Pre-Game State, waiting 1 minute')
            self._draw_pregame()
            t.sleep(60)
        # tuesday 06h00 UTC until week change
        elif (time.weekday() == 1 and time.hour >= 6) or (1 < time.weekday() < 4):
            debug.info('Final State, waiting 6 hours')
            self._draw_post_game()
            # sleep 6 hours
            # may as well just unplug or turn off tbh
            t.sleep(21600)
        # friday after 00h15 UTC until tuesday 06h00 UTC 
        else:
            debug.info('Live State, checking every 10s')
            # Draw the current game
            self._draw_game()

    def __render_off_season(self):
        debug.info('ping_off_season')
        self._draw_off_season()
        t.sleep(86400) # sleep 24 hours

    # need to keep working on this
    def _draw_pregame(self):
        # get the matchup
        # get the matchup pics and resize them to 32x32
        # don't you love how messy this is? boy
        if self.data.matchup:
            matchup = self.data.matchup
            opp_av = matchup['opp_av']
            user_av = matchup['user_av']
            if opp_av is None:
                opp_av = 'noneLogo.png'
            if user_av is None:
                user_av = 'noneLogo.png'
            week = self.data.week
            if week == 0:
                week = 1
            game_date = 'WEEK {}'.format(week)
            vs = 'VS'
            user_name = matchup['user_name']
            opp_name = matchup['opp_name']
            user_team = matchup.get('user_team')
            opp_team = matchup.get('opp_team')
            # choose team names that fit
            if user_team and len(user_team) < 13:
                user_name = user_team
            if opp_team and len(opp_team) < 13:
                opp_name = opp_team
            game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 32)
            vs_pos = center_text(self.font_vs.getsize(vs)[0], 32)
            self.draw.multiline_text((game_date_pos, 0), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((vs_pos + 1, 14), vs, fill=(255, 255, 255), font=self.font_vs, align="center")
            if len(user_name) > 12 or len(opp_name) > 12:
                if self.data.platform == "yahoo":
                    # Open the logo image file
                    opp_logo = Image.open('logos/{}.jpg'.format(opp_av)).resize((23, 23), Image.BOX)
                    user_logo = Image.open('logos/{}.jpg'.format(user_av)).resize((23, 23), Image.BOX)
                elif self.data.platform == "espn":
                    opp_logo = Image.open('logos/{}'.format(opp_av)).resize((23, 23), Image.BOX)
                    user_logo = Image.open('logos/{}'.format(user_av)).resize((23, 23), Image.BOX)
                else:
                    # try png for sleeper
                    opp_logo = Image.open('logos/{}.png'.format(opp_av)).resize((23, 23), Image.BOX)
                    user_logo = Image.open('logos/{}.png'.format(user_av)).resize((23, 23), Image.BOX)
                # Set the position of each logo on screen.
                opp_team_logo_pos = { "x": 0, "y": 9 }
                user_team_logo_pos = { "x": 41, "y": 9 }
            else:
                self.draw.multiline_text((0, 6), opp_name, fill=(255, 255, 255), font=self.font_mini, align="left")
                self.draw.multiline_text((self.width - self.font_mini.getsize(user_name)[0], self.height - self.font_mini.getsize(user_name)[1]), user_name, fill=(255, 255, 255), font=self.font_mini, align="left")
                # Open the logo image file
                if self.data.platform == "yahoo":
                    # Open the logo image file
                    opp_logo = Image.open('logos/{}.jpg'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}.jpg'.format(user_av)).resize((19, 19), Image.BOX)
                elif self.data.platform == "espn":
                    opp_logo = Image.open('logos/{}'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}'.format(user_av)).resize((19, 19), Image.BOX)
                else:
                    # try png for sleeper
                    opp_logo = Image.open('logos/{}.png'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}.png'.format(user_av)).resize((19, 19), Image.BOX)
                # Set the position of each logo on screen.
                opp_team_logo_pos = { "x": 0, "y": 13 }
                user_team_logo_pos = { "x": 45, "y": 7 }
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(opp_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
            self.canvas.SetImage(user_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            t.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):
        self.data.refresh_matchup()
        matchup = self.data.matchup
        opp_av = matchup['opp_av']
        user_av = matchup['user_av']
        if opp_av is None:
            opp_av = 'noneLogo.png'
        if user_av is None:
            user_av = 'noneLogo.png'
        user_score = matchup.get('user_score')
        opp_score = matchup.get('opp_score')
        self.data.needs_refresh = True
        extra_sleep = 0
        while True:
            # Refresh the data
            if self.data.needs_refresh and self.data.check_scores:
                debug.info('Refresh game matchup')
                extra_sleep = 0
                self.data.refresh_scores()
                self.data.needs_refresh = False
            else:
                debug.info('Not refreshing, will update in 1 minute')
                extra_sleep = 40
                self.data.check_if_playing()
                self.data.needs_refresh = True
            if self.data.matchup:
                # colours
                opp_colour = (255, 255, 255)
                user_colour = (255, 255, 255)
                matchup = self.data.matchup
                game_date = 'WEEK {}'.format(self.data.week)
                # small increase in score
                if matchup['user_score'] > user_score:
                    user_colour = (165, 200, 50)
                if matchup['opp_score'] > opp_score:
                    opp_colour = (165, 200, 50)
                # decrease in score
                if matchup['user_score'] < user_score:
                    user_colour = (175, 25, 25)
                if matchup['opp_score'] < opp_score:
                    opp_colour = (175, 25, 25)
                # big play! 5+ points for someone, turn it gold
                if matchup.get('user_score', 0) > (user_score + 5) or matchup.get('opp_score', 0) > (opp_score + 5):
                    self._draw_big_play()
                if matchup['user_score'] > user_score + 5:
                    user_colour = (255, 215, 0)
                if matchup['opp_score'] > opp_score + 5:
                    opp_colour = (255, 215, 0)
                # Using big and small numbers
                opp_big, opp_small = divmod(matchup['opp_score'], 1)
                opp_big = int(opp_big)
                opp_small = int(round(opp_small, 2) * 100)
                if opp_small < 10:
                    opp_small = '0' + str(opp_small)
                    opp_small_score = '{}'.format(opp_small)
                else:
                    opp_small_score = '{0:02d}'.format(opp_small)
                user_big, user_small = divmod(matchup['user_score'], 1)
                user_big = int(user_big)
                user_small = int(round(user_small, 2) * 100)
                if user_small < 10:
                    user_small = '0' + str(user_small)
                    user_small_score = '{}'.format(user_small)
                else:
                    user_small_score = '{0:02d}'.format(user_small)
                opp_diff = '{:0.2f}'.format(abs(opp_score - matchup['opp_score']))
                user_diff = '{:0.2f}'.format(abs(user_score - matchup['user_score']))
                opp_big_size = self.font.getsize(str(opp_big))[0]
                opp_small_size = self.font_mini.getsize(str(opp_small))[0]
                user_big_size = self.font.getsize(str(user_big))[0]
                user_small_size = self.font_mini.getsize(str(user_small))[0]
                user_diff_size = self.font_mini.getsize(user_diff)[0]
                opp_diff_size = self.font_mini.getsize(opp_diff)[0]
                # this is bad form I know but idc come at me I'll fix it eventually when I'm not tired and trying random chit
                opp_big_score = '{}'.format(opp_big)
                user_big_score = '{}'.format(user_big)
                # trying to centre them to make it a bit more a e s t h e t i c (essentially adding padding)
                left_offset = int(math.floor(opp_big / 100)) # ((self.width / 2) - (opp_big_size + opp_small_size)) / 2 - 2
                # eventually may colour differently depending on score advantage
                self.draw.multiline_text((left_offset, 19), opp_big_score, fill=opp_colour, font=self.font, align="left")
                self.draw.multiline_text((opp_big_size + left_offset, 19), opp_small_score, fill=opp_colour, font=self.font_mini, align="left")
                self.draw.multiline_text((self.width - user_small_size - user_big_size, 19), user_big_score, fill=user_colour, font=self.font, align="right")
                self.draw.multiline_text((self.width - user_small_size, 19), user_small_score, fill=user_colour, font=self.font_mini, align="right")
                # diffs
                if abs(opp_score - matchup['opp_score']) > 0:
                    self.draw.multiline_text((21, 6), opp_diff, fill=opp_colour, font=self.font_mini, align="left")
                if abs(user_score - matchup['user_score']) > 0:
                    self.draw.multiline_text((self.width - 20 - user_diff_size, 12), user_diff, fill=user_colour, font=self.font_mini, align="right")
                # Set the projections on the screen?
                game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 32)
                # score_position = center_text(self.font.getsize(score)[0], 32)
                # Set the position of each logo on screen.
                self.draw.multiline_text((game_date_pos, -1), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
                if self.data.platform == "yahoo":
                    # Open the logo image file
                    opp_logo = Image.open('logos/{}.jpg'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}.jpg'.format(user_av)).resize((19, 19), Image.BOX)
                elif self.data.platform == "espn":
                    opp_logo = Image.open('logos/{}'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}'.format(user_av)).resize((19, 19), Image.BOX)
                else:
                    # try png for sleeper/espn (hopefully)
                    opp_logo = Image.open('logos/{}.png'.format(opp_av)).resize((19, 19), Image.BOX)
                    user_logo = Image.open('logos/{}.png'.format(user_av)).resize((19, 19), Image.BOX)
                # Set the position of each logo on screen.
                opp_team_logo_pos = { "x": 0, "y": 0 }
                user_team_logo_pos = { "x": 45, "y": 0 }
                # Put the data on the canvas
                self.canvas.SetImage(self.image, 0, 0)
                # Put the images on the canvas
                self.canvas.SetImage(opp_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
                self.canvas.SetImage(user_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                # Save the scores.
                opp_score = matchup['opp_score']
                user_score = matchup['user_score']
                self.data.needs_refresh = True
                t.sleep(10 + extra_sleep)
            else:
                # this doesn't work lul need 2 fix
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 30s.
                self.draw.line((0, self.height) + (self.width, self.height), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                t.sleep(30)

    # I think this is fine?
    def _draw_post_game(self):
        self.data.refresh_matchup()
        if self.data.matchup != 0:
            matchup = self.data.matchup
            opp_av = matchup['opp_av']
            user_av = matchup['user_av']
            if opp_av is None:
                opp_av = 'noneLogo.png'
            if user_av is None:
                user_av = 'noneLogo.png'
            # testing
            # Using big and small numbers
            # this is so so so terrible, I know but idc come at me I'll fix it eventually when I'm not tired and trying random chit
            opp_big, opp_small = divmod(matchup['opp_score'], 1)
            opp_big = int(opp_big)
            opp_small = int(round(opp_small, 2) * 100)
            if opp_small < 10:
                opp_small = '0' + str(opp_small)
                opp_small_score = '{}'.format(opp_small)
            else:
                opp_small_score = '{0:02d}'.format(opp_small)
            user_big, user_small = divmod(matchup['user_score'], 1)
            user_big = int(user_big)
            user_small = int(round(user_small, 2) * 100)
            if user_small < 10:
                user_small = '0' + str(user_small)
                user_small_score = '{}'.format(user_small)
            else:
                user_small_score = '{0:02d}'.format(user_small)
            opp_big_size = self.font.getsize(str(opp_big))[0]
            opp_small_size = self.font_mini.getsize(str(opp_small))[0]
            user_big_size = self.font.getsize(str(user_big))[0]
            user_small_size = self.font_mini.getsize(str(user_small))[0]
            user_big_score = '{}'.format(user_big)
            opp_big_score = '{}'.format(opp_big)
            # trying to centre them to make it a bit more a e s t h e t i c (essentially adding padding)
            left_offset = int(math.floor(opp_big / 100))
            # end testing
            # Prepare the data
            game_date = 'WEEK {}'.format(self.data.week)
            result = ''
            opp_colour = (255, 255, 255)
            user_colour = (255, 255, 255)
            if matchup['opp_score'] > matchup['user_score']:
                result = 'LOSS'
                opp_colour = (25, 200, 25)
                user_colour = (200, 25, 25)
            else:
                result = 'WIN'
                opp_colour = (200, 25, 25)
                user_colour = (25, 200, 25)
            self.draw.multiline_text((left_offset, 19), opp_big_score, fill=opp_colour, font=self.font, align="left")
            self.draw.multiline_text((opp_big_size + left_offset, 19), opp_small_score, fill=opp_colour, font=self.font_mini, align="left")
            self.draw.multiline_text((self.width - user_small_size - user_big_size, 19), user_big_score, fill=user_colour, font=self.font, align="right")
            self.draw.multiline_text((self.width - user_small_size, 19), user_small_score, fill=user_colour, font=self.font_mini, align="right")
            # Set the position of the information on screen.
            game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 32)
            result_pos = center_text(self.font_res.getsize(result)[0], 32) # this was font_mini before, was that on purpose?
            # result_pos = center_text(self.font_mini.getsize(result)[0], 32)
            # Draw the text on the Data image.
            self.draw.multiline_text((game_date_pos, 0), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((result_pos, 9), result, fill=(255, 255, 255), font=self.font_res, align="center")
            # Open the logo image file
            if self.data.platform == "yahoo":
                # Open the logo image file
                opp_logo = Image.open('logos/{}.jpg'.format(opp_av)).resize((19, 19), Image.BOX)
                user_logo = Image.open('logos/{}.jpg'.format(user_av)).resize((19, 19), Image.BOX)
            elif self.data.platform == "espn":
                opp_logo = Image.open('logos/{}'.format(opp_av)).resize((19, 19), Image.BOX)
                user_logo = Image.open('logos/{}'.format(user_av)).resize((19, 19), Image.BOX)
            else:
                # try png for sleeper/espn (hopefully)
                opp_logo = Image.open('logos/{}.png'.format(opp_av)).resize((19, 19), Image.BOX)
                user_logo = Image.open('logos/{}.png'.format(user_av)).resize((19, 19), Image.BOX)
            # Set the position of each logo on screen.
            opp_team_logo_pos = { "x": 0, "y": 0 }
            user_team_logo_pos = { "x": 45, "y": 0 }
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(opp_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
            self.canvas.SetImage(user_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            # (Need to make the screen runs) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            t.sleep(60)  # sleep for 1 min

    def _draw_big_play(self):
        debug.info('big play woo!')
        # Load the gif file
        im = Image.open("Assets/big_play_animation.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        play = True
        # I think this code was originally made to repeat the gif 5 times, but I need to test it
        # thus the stupid
        # also, it works, so why break it when I'm literally learning python by the seat of my pants?
        while play:
            try:
                im.seek(frameNo)
            except EOFError:
                play = False
            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.02)

    def _draw_off_season(self):
        # Refresh canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        off_pos = center_text(self.font.getsize("OFF")[0], 32)
        szn_pos = center_text(self.font.getsize("SEASON")[0], 32)
        self.draw.multiline_text((off_pos,3), "OFF", fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((szn_pos, self.font.getsize("SEASON")[1]+4), "SEASON", fill=(255, 255, 255), font=self.font, align="center")
        self.canvas.SetImage(self.image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
