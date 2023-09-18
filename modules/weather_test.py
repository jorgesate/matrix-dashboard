from pyowm.owm import OWM
import time

lat = 40.4165
lon = -3.7026

mgr = OWM('51834c6ffe6c0eaad22e790016c898a6').weather_manager()
message = mgr.one_call(lat = lat, lon = lon)

print(message)