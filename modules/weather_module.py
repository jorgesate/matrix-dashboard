from pyowm.owm import OWM
from threading import Thread
from queue import LifoQueue
import time

class WeatherModule:
    def __init__(self, config):
        self.one_call = None
        self.queue = LifoQueue()

        if config != None and 'OWM' in config and 'token' in config['OWM'] and config['OWM']['token'] != "" and 'lat' in config['OWM'] and 'lon' in config['OWM']:   
            self.mgr = OWM(config['OWM']['token']).weather_manager()
            self.thread = Thread(target = update_weather, args=(self.mgr, self.queue, float(config['OWM']['lat']), float(config['OWM']['lon']),))
            self.thread.start()
        else:
            print("[Weather Module] Empty OWM API Token")

    def getWeather(self):
        if not self.queue.empty():
            self.one_call = self.queue.get()
            self.queue.queue.clear()
        return self.one_call

def update_weather(mgr, weather_queue, lat, lon):
    lastTimeCall = 0
    while True:
        currTime = time.time()
        if (currTime - lastTimeCall >= 1000):
            try:
                lastTimeCall = currTime
                # print("Trying to get weather")
                message = mgr.one_call(lat = lat, lon = lon)
                # print(message)
                weather_queue.put(message)
                
            except Exception:
                # print("Exception trying to get weather")
                pass