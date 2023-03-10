#!/usr/bin/env python
import sys, os, time, copy, inspect
from InputStatus import InputStatusEnum
from gpiozero import Button
import configparser
from PIL import Image

import select

from apps_v2 import main_screen, notion_v2, weather, life, spotify_player, gif_viewer
from modules import weather_module, spotify_module

sys.path.append("/home/pi/rpi-rgb-led-matrix/bindings/python")
from rgbmatrix import RGBMatrix, RGBMatrixOptions

def main():

    # print("Starting matrix-screen controller: \n")
    brightness = 100
    brightness_idx = 0
    brightness_values = [100, 90, 80, 70, 60]
    displayOn = True

    config = configparser.ConfigParser()
    parsed_configs = config.read('/home/pi/matrix-screen/config.ini')
    if len(parsed_configs) == 0:
        # print("no config file found")
        sys.exit()

    canvas_width = config.getint('System', 'canvas_width', fallback=64)
    canvas_height = config.getint('System', 'canvas_height', fallback=32)

    black_screen = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))

    # Buttons config
    inputStatusDict = {"value" : InputStatusEnum.NOTHING}
    
    next_bt = 25
    sw_bt = 10
    prev_bt = 9
    brig_bt = 11

    encButton = Button(sw_bt, pull_up = False)
    encButton.when_pressed = lambda button : encButtonFunc(button, inputStatusDict, isHorizontalDict)

    encNext = Button(next_bt, pull_up = False)
    encNext.when_pressed = lambda button : nextButtonFunc(button, inputStatusDict)
    encPrev = Button(prev_bt, pull_up = False)
    encPrev.when_pressed = lambda button : previousButtonFunc(button, inputStatusDict)

    butBright = Button(brig_bt, pull_up = False)
    butBright.when_pressed = lambda: change_brightness()

    # tilt_switch = Button(tilt, pull_up = True)
    isHorizontalDict = {'value': True}
    # tilt_switch.when_pressed = lambda button : tilt_callback(button, isHorizontalDict)
    # tilt_switch.when_released = lambda button : tilt_callback(button, isHorizontalDict)

    def toggle_display():
        nonlocal displayOn
        displayOn = not displayOn
        # print("Display On: " + str(displayOn))

    def increase_brightness():
        nonlocal brightness
        brightness = min(100, brightness + 10)

    def decrease_brightness():
        nonlocal brightness
        brightness = max(50, brightness - 10)
    
    def change_brightness():
        nonlocal brightness
        nonlocal brightness_idx
        brightness_idx = brightness_idx + 1
        if brightness_idx > 4:
            brightness_idx = 0
        brightness = brightness_values[brightness_idx]

    current_app_idx = 0
    def switch_next_app():
        nonlocal current_app_idx
        current_app_idx += 1
    
    def switch_prev_app():
        nonlocal current_app_idx
        current_app_idx -= 1

    callbacks = {
                    'toggle_display' : toggle_display,
                    'switch_next_app' : switch_next_app,
                    'switch_prev_app' : switch_prev_app,
                    'change_brightness': change_brightness,
                    'increase_brightness': increase_brightness,
                    'decrease_brightness': decrease_brightness
                }
    
    modules =   {
                    'weather' : weather_module.WeatherModule(config),
                    'spotify' : spotify_module.SpotifyModule(config)
                }

    app_list = [main_screen.MainScreen(config, modules, callbacks),
                gif_viewer.GifScreen(config, modules, callbacks),
                notion_v2.NotionScreen(config, modules, callbacks),
                weather.WeatherScreen(config, modules, callbacks),
                spotify_player.SpotifyScreen(config, modules, callbacks)]
    # life.GameOfLifeScreen(config, modules, callbacks),

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.brightness = brightness
    options.pixel_mapper_config = ""
    options.gpio_slowdown = 2
    options.pwm_lsb_nanoseconds = 130
    options.limit_refresh_rate_hz = 60
    options.led_rgb_sequence = "RGB"
    options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
    options.drop_privileges = False
    matrix = RGBMatrix(options = options)

    isHorizontalSnapshot = True
    
    # MAIN LOOP

    while(True):

        inputStatusSnapshot = copy.copy(inputStatusDict['value'])
        inputStatusDict['value'] = InputStatusEnum.NOTHING
        isHorizontalSnapshot = copy.copy(isHorizontalDict['value'])

        # while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        #     cmd = sys.stdin.readline()
        #     if cmd:
        #         # print("detected: " + cmd)
        #         if cmd == 'SP\n':
        #             inputStatusSnapshot = InputStatusEnum.SINGLE_PRESS
        #         elif cmd == 'DP\n':
        #             inputStatusSnapshot = InputStatusEnum.DOUBLE_PRESS
        #         elif cmd == 'TP\n':
        #             inputStatusSnapshot = InputStatusEnum.TRIPLE_PRESS
        #         elif cmd == 'LP\n':
        #             inputStatusSnapshot = InputStatusEnum.LONG_PRESS
        #         elif cmd == 'EI\n':
        #             inputStatusSnapshot = InputStatusEnum.NEXT_SP
        #         elif cmd == 'ED\n':
        #             inputStatusSnapshot = InputStatusEnum.PREVIOUS_SP
        #         elif cmd == 'HO\n':
        #             isHorizontalSnapshot = True
        #         elif cmd == 'VE\n':
        #             isHorizontalSnapshot = False
        #         elif cmd == 'BC\n':
        #             change_brightness()

        frame = app_list[current_app_idx % len(app_list)].generate(isHorizontalSnapshot, inputStatusSnapshot)
        if not displayOn:
            frame = black_screen
        
        matrix.brightness = brightness
        matrix.SetImage(frame)
        time.sleep(0.05)

def encButtonFunc(enc_button, inputStatusDict, isHorizontalDict):
    start_time = time.time()
    time_diff = 0
    hold_time = 1
    
    while enc_button.is_active and (time_diff < hold_time):
        time_diff = time.time() - start_time

    if (time_diff >= hold_time):
        # print("long press detected")
        inputStatusDict['value'] = InputStatusEnum.LONG_PRESS
    else:
        enc_button.when_pressed = None
        start_time = time.time()
        while (time.time() - start_time <= 0.3):
            time.sleep(0.1)
            if (enc_button.is_pressed):
                time.sleep(0.1)
                new_start_time = time.time()
                while (time.time() - new_start_time <= 0.3):
                    time.sleep(0.1)
                    if (enc_button.is_pressed):
                        # print("triple press detected")
                        inputStatusDict['value'] = InputStatusEnum.TRIPLE_PRESS
                        enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict, isHorizontalDict)
                        tilt_callback(isHorizontalDict)
                        return
                # print("double press detected")
                inputStatusDict['value'] = InputStatusEnum.DOUBLE_PRESS
                enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict, isHorizontalDict)
                return
        # print("single press detected")
        inputStatusDict['value'] = InputStatusEnum.SINGLE_PRESS
        enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict, isHorizontalDict)
        return

def nextButtonFunc(next_button, inputStatusDict):
    start_time = time.time()
    time_diff = 0
    hold_time = 1
    
    while next_button.is_active and (time_diff < hold_time):
        time_diff = time.time() - start_time

    if (time_diff >= hold_time):
        # print("long press detected")
        inputStatusDict['value'] = InputStatusEnum.NOTHING
    else:
        next_button.when_pressed = None
        start_time = time.time()
        while (time.time() - start_time <= 0.3):
            time.sleep(0.1)
            if (next_button.is_pressed):
                # print("next double press detected")
                inputStatusDict['value'] = InputStatusEnum.NEXT_DP
                next_button.when_pressed = lambda button : nextButtonFunc(button, inputStatusDict)
                return
        # print("next single press detected")
        inputStatusDict['value'] = InputStatusEnum.NEXT_SP
        next_button.when_pressed = lambda button : nextButtonFunc(button, inputStatusDict)
        return

def previousButtonFunc(prev_button, inputStatusDict):
    start_time = time.time()
    time_diff = 0
    hold_time = 1
    
    while prev_button.is_active and (time_diff < hold_time):
        time_diff = time.time() - start_time

    if (time_diff >= hold_time):
        # print("long press detected")
        inputStatusDict['value'] = InputStatusEnum.NOTHING
    else:
        prev_button.when_pressed = None
        start_time = time.time()
        while (time.time() - start_time <= 0.3):
            time.sleep(0.1)
            if (prev_button.is_pressed):
                # print("prev double press detected")
                inputStatusDict['value'] = InputStatusEnum.PREVIOUS_DP
                prev_button.when_pressed = lambda button : previousButtonFunc(button, inputStatusDict)
                return
        # print("prev single press detected")
        inputStatusDict['value'] = InputStatusEnum.PREVIOUS_SP
        prev_button.when_pressed = lambda button : previousButtonFunc(button, inputStatusDict)
        return

def tilt_callback(isHorizontalDict):
    
    isHorizontalDict['value'] = not isHorizontalDict['value']

def reduceFrameToString(frame):
    res = frame.flatten()
    return ' '.join(map(str, res))

try:
    main()
except KeyboardInterrupt:
    # print('Interrupted with Ctrl-C')
    sys.exit(0)
    