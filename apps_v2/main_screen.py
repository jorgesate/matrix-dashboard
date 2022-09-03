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
        self.cycle_time = config.getint('Main Screen', 'cycle_time', fallback = 20)
        self.use_24_hour = config.getboolean('Main Screen', 'use_24_hour', fallback = True)

        self.vertical = pomodoro.PomodoroScreen(config, modules, default_actions)

        self.lastGenerateCall = None
        self.on_cycle = True
        self.one_call = None

        self.cycles = 10

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
                    
        self.theme_list = [self.generateBladerunner,
                           self.generateCity,
                           self.generateForestSunset,
                           self.generateDeathStar,
                           self.generateDroids,
                           self.generateFuture,
                           self.generateRetroVice,
                           self.generateDune,
                           self.generateSakura,
                           self.generateSamurai,
                           self.generateForest]

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
        if (time.time() - self.lastGenerateCall >= self.cycle_time):
            self.on_cycle = not self.on_cycle
            self.lastGenerateCall = time.time()

        frame = self.theme_list[self.currentIdx % len(self.theme_list)]()
        
        if (self.selectMode):
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0,0,self.canvas_width-1,self.canvas_height-1), outline=white)
        
        return frame

    def generateCity(self):

        # Get background image
        frame = self.bgs['city'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 2
        y_time = 2
        x_date = 45
        y_date = 2

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
        draw.text((x_time, y_time), padToTwoDigit(hours), black, font=self.font)
        draw.text((x_time + 7, y_time), ":", black, font=self.font)
        draw.text((x_time + 10, y_time), padToTwoDigit(minutes), black, font=self.font)
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), black, font=self.font)
            draw.text((x_date + 7, y_date), ".", black, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), black, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), black, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), blueish, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateForestSunset(self):

        # Get background image
        frame = self.bgs['forest_sunset'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 3
        y_time = 3
        x_date = 25
        y_date = 3

        # Colors
        time_color = (39, 4, 74)
        temperature_color = (100, 11, 149)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), time_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", time_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), time_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), time_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateDeathStar(self):

        # Get background image
        frame = self.bgs['death_star'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 23
        y_time = 3
        x_date = 45
        y_date = 3

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
        draw.text((x_time, y_time), padToTwoDigit(hours), death_star_green, font=self.font)
        draw.text((x_time + 7, y_time), ":", death_star_green, font=self.font)
        draw.text((x_time + 10, y_time), padToTwoDigit(minutes), death_star_green, font=self.font)
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), death_star_green, font=self.font)
            draw.text((x_date + 7, y_date), ".", death_star_green, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), death_star_green, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), death_star_green, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), death_star_dark_green, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateRetroVice(self):

        # Get background image
        frame = self.bgs['retro_vice'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 12
        y_time = 2
        x_date = 34
        y_date = 2

        # Colors
        time_color = (235, 217, 199)
        temperature_color = (42, 15, 52)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), time_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", time_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), time_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), time_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateBladerunner(self):

        # Get background image
        frame = self.bgs['bladerunner'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 28
        y_time = 3
        x_date = 33
        y_date = 10

        # Colors
        time_color = (174, 148, 200)
        temperature_color = (222, 160, 185)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), time_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", time_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), time_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), time_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame
    
    def generateDroids(self):

        # Get background image
        frame = self.bgs['droids'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 8
        y_time = 3
        x_date = 41
        y_date = 3

        # Colors
        time_color = (223, 180, 89)
        temperature_color = (56, 101, 208)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), temperature_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", temperature_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), temperature_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), temperature_color, font=self.font)
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), temperature_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateFuture(self):

        # Get background image
        frame = self.bgs['future'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 8
        y_time = 1
        x_date = 41
        y_date = 1

        # Colors
        color_1 = (237, 85, 35)
        color_2 = (244, 121, 34)
        color_3 = (248, 183, 25)
        color_4 = (252, 218, 3)

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
        draw.text((x_time, y_time), padToTwoDigit(hours), color_1, font=self.font)
        draw.text((x_time + 7, y_time), ":", color_1, font=self.font)
        draw.text((x_time + 10, y_time), padToTwoDigit(minutes), color_2, font=self.font)
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), color_3, font=self.font)
            draw.text((x_date + 7, y_date), ".", color_3, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), color_4, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), color_3, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), color_4, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateSamurai(self):

        # Get background image
        frame = self.bgs['samurai'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 3
        y_time = 3
        x_date = 44
        y_date = 3

        # Colors
        time_color = (28, 25, 45)
        temperature_color = (68, 15, 56)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), temperature_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", temperature_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), temperature_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), temperature_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame
                             
    def generateSakura(self):
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

        frame = self.bgs['sakura'].copy()
        draw = ImageDraw.Draw(frame)

        draw.text((3, 6), padToTwoDigit(hours), light_pink, font=self.font)
        draw.text((10, 6), ":", light_pink, font=self.font)
        draw.text((13, 6), padToTwoDigit(minutes), light_pink, font=self.font)
        
        if (self.on_cycle):
            #date
            draw.text((23, 6), padToTwoDigit(month), dark_pink, font=self.font)
            draw.text((30, 6), ".", dark_pink, font=self.font)
            draw.text((33, 6), padToTwoDigit(day), dark_pink, font=self.font)
        else:
            #dayOfWeek
            draw.text((23, 6), dayOfWeekToText(dayOfWeek), dark_pink, font=self.font)
            #weather
            weather = self.modules['weather']
            one_call = weather.getWeather()
            if (one_call != None):
                curr_temp = round(one_call.current.temperature('celsius')['temp'])
                draw.text((33, 6), padToTwoDigit(curr_temp), white, font=self.font)
                #draw.point((41,6), fill=white)
        
        return frame

    def generateDune(self):

        # Get background image
        frame = self.bgs['dune'].copy()
        draw = ImageDraw.Draw(frame)

        # Coordinates
        x_time = 45
        y_time = 2
        x_date = 45
        y_date = 10

        # Colors
        time_color = (48, 66, 87)
        temperature_color = (29, 14, 8)

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
        
        if (self.on_cycle):
            #date
            draw.text((x_date, y_date), padToTwoDigit(day), temperature_color, font=self.font)
            draw.text((x_date + 7, y_date), ".", temperature_color, font=self.font)
            draw.text((x_date + 10, y_date), padToTwoDigit(month), temperature_color, font=self.font)
        else:
            #dayOfWeek
            draw.text((x_date, y_date), dayOfWeekToText(dayOfWeek), temperature_color, font=self.font)
            #weather
            weather = self.modules['weather']
            if (self.cycles > 5):
                self.one_call = weather.getWeather()
                if (self.one_call != None):
                    curr_temp = round(self.one_call.current.temperature('celsius')['temp'])
                    draw.text((x_date + 10, y_date), padToTwoDigit(curr_temp), temperature_color, font=self.font)
                self.cycles = 0
            else:
                self.cycles = self.cycles + 1
        
        return frame

    def generateForest(self):
        frame = self.bgs['forest'].copy()
        return frame

def padToTwoDigit(num):
    if num < 10:
        return "0" + str(num)
    else:
        return str(num)

def dayOfWeekToText(dayOfWeek):
    dayOfWeekText = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]

    return dayOfWeekText[dayOfWeek]