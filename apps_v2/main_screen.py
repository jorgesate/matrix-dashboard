from pyexpat.model import XML_CTYPE_MIXED
from InputStatus import InputStatusEnum
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from dateutil import tz
import time

from apps_v2 import pomodoro

black = (0, 0, 0)
light_pink = (255,219,218)
dark_pink = (219,127,142)
white = (230,255,255)
red = (230, 0, 0)
blueish = (10, 0, 230)
death_star_green = (172, 245, 251)
death_star_dark_green = (19, 148, 179)
salmon = (255,150,162)
tan = (255,205,178)
orange_tinted_white = (248,237,235)
washed_out_navy = (109,104,117)


class MainScreen:
    def __init__(self, config, modules, default_actions):
        self.font = ImageFont.truetype("/home/pi/matrix-screen/fonts/tiny.otf", 5)
        self.modules = modules
        self.default_actions = default_actions

        self.canvas_width = config.getint('System', 'canvas_width', fallback = 64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback = 32)
        self.cycle_time_generate = config.getint('Main Screen', 'cycle_time', fallback = 20)
        self.cycle_time_weather = config.getint('Main Screen', 'cycle_time', fallback = 120)
        self.use_24_hour = config.getboolean('Main Screen', 'use_24_hour', fallback = True)

        self.vertical = pomodoro.PomodoroScreen(config, modules, default_actions)

        self.lastGenerateCall = None
        self.lastWeatherCall = 0
        self.on_cycle_generate = True
        self.on_cycle_weather = True

        self.one_call = None
        self.curr_temp = 0

        self.bgs = {'bladerunner': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/bladerunner.png').convert("RGB"),
                    'city': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/city.png').convert("RGB"),
                    'forest_sunset': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/forest-sunset.png').convert("RGB"),
                    'death_star': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/death-star.png').convert("RGB"),
                    'droids': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/droids.png').convert("RGB"),
                    'future': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/future.png').convert("RGB"),
                    'retro_vice': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/retro_vice.png').convert("RGB"),
                    'sakura': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/sakura-bg.png').convert("RGB"),
                    'forest': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/forest-bg.png').convert("RGB"),
                    'dune': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/dune.png').convert("RGB"),
                    'samurai': Image.open('/home/pi/matrix-screen/apps_v2/res/main_screen/samurai.png').convert("RGB")}
                    
        self.arguments = [('bladerunner',   28, 3, 33, 10, (174, 148, 200), (222, 160, 185)),
                          ('city',          2, 2, 45, 2,   (0, 0, 0),       (10, 0, 230)),
                          ('forest_sunset', 3, 3, 25, 3,   (39, 4, 74),     (100, 11, 149)),
                          ('death_star',    23, 3, 45, 3,  (172, 245, 251), (19, 148, 179)),
                          ('droids',        8, 3, 41, 3,   (223, 180, 89),  (56, 101, 208)),
                          ('future',        8, 1, 41, 1,   (237, 85, 35),   (252, 218, 3)),
                          ('retro_vice',    12, 2, 34, 2,  (235, 217, 199), (42, 15, 52)),
                          ('sakura',        3, 6, 23, 6,   (255,219,218),   (230,255,255)),
                          ('forest',        100, 100, 100, 100, (0, 0, 0),  (0, 0, 0)),
                          ('dune',          45, 2, 45, 10,   (48, 66, 87),  (29, 14, 8)),
                          ('samurai',       3, 3, 44, 3,   (28, 25, 45),    (68, 15, 56))]
        
        self.currentIdx = 0
        self.selectMode = False

        self.queued_frames = []
    
    def generate(self, isHorizontal, inputStatus):
        if not isHorizontal:
            return self.vertical.generate(isHorizontal, inputStatus)
        
        if (inputStatus == InputStatusEnum.LONG_PRESS):
            self.selectMode = not self.selectMode

        if self.selectMode:
            if (inputStatus is InputStatusEnum.NEXT_SP):
                self.currentIdx += 1
                self.queued_frames = []
            elif (inputStatus is InputStatusEnum.PREVIOUS_SP):
                self.currentIdx -= 1
                self.queued_frames = []
        else:
            if (inputStatus is InputStatusEnum.SINGLE_PRESS):
                self.default_actions['toggle_display']()
            elif (inputStatus is InputStatusEnum.NEXT_SP):
                self.default_actions['switch_next_app']()
            elif (inputStatus is InputStatusEnum.PREVIOUS_SP):
                self.default_actions['switch_prev_app']()
            elif (inputStatus is InputStatusEnum.NEXT_DP):
                self.default_actions['increase_brightness']()
            elif (inputStatus is InputStatusEnum.PREVIOUS_DP):
                self.default_actions['decrease_brightness']()

        if (self.lastGenerateCall == None):
            self.lastGenerateCall = time.time()
        if (time.time() - self.lastGenerateCall >= self.cycle_time_generate):
            self.on_cycle_generate = not self.on_cycle_generate
            self.lastGenerateCall = time.time()

        # Update weather each [self.cycle_time_weather] seconds and on first run
        weather = self.modules['weather']
        if (self.lastWeatherCall == 0):
            self.one_call = weather.getWeather()
            if (self.one_call != None):
                self.curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                self.lastWeatherCall = time.time()
        if (time.time() - self.lastWeatherCall >= self.cycle_time_weather):
            self.one_call = weather.getWeather()
            if (self.one_call != None):
                self.curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                self.lastWeatherCall = time.time()

        # Frame generation
        frame = self.generateFrame(*self.arguments[self.currentIdx % len(self.arguments)])
        
        if (self.selectMode):
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0,0,self.canvas_width-1,self.canvas_height-1), outline=white)
        
        return frame

    def generateFrame(self, frame_name, x_time, y_time, x_date, y_date, time_color, temperature_color):

        # Get background image
        frame = self.bgs[frame_name].copy()
        draw = ImageDraw.Draw(frame)

        # Get time and date
        currentTime = datetime.now(tz=tz.tzlocal())
        month = currentTime.month
        day = currentTime.day
        dayOfWeek = currentTime.weekday()
        hours = currentTime.hour
        if not self.use_24_hour:
            hours = hours % 12
            if (hours == 0):
                hours += 12 
        minutes = currentTime.minute

        # Draw time
        draw.text((x_time, y_time), padToTwoDigit(hours), time_color, font=self.font)
        draw.text((x_time + 7, y_time), ":", time_color, font=self.font)
        draw.text((x_time + 10, y_time), padToTwoDigit(minutes), time_color, font=self.font)
        
        if (self.on_cycle_generate):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), time_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", time_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), time_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), time_color, font=self.font)
            #weather
            draw.text((x_date + 10, y_date), padToTwoDigit(self.curr_temp), temperature_color, font=self.font)

        return frame

def padToTwoDigit(num):
    if num < 10:
        return "0" + str(num)
    else:
        return str(num)

def dayOfWeekToText(dayOfWeek):
    dayOfWeekText = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]

    return dayOfWeekText[dayOfWeek]