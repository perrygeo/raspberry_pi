import time
from datetime import datetime
import sys
from pprint import pprint

try:
    import conflocal as config
except ImportError:
    import config

import ultrasonicRanger
import AirQualitySensorLibrary as aq
import extendedPlants
import RPi.GPIO as GPIO
import psycopg2

sys.path.append("./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15")
sys.path.append("./SDL_Pi_GroveDigitalExtender")
sys.path.append("./SDL_Pi_HDC1000")
sys.path.append("./SDL_Pi_SI1145")

import SDL_Pi_HDC1000  # noqa 402
import SDL_Pi_SI1145  # noqa 402
from SDL_Adafruit_ADS1x15 import ADS1x15  # noqa 402

# 4 Channel ADC ADS1115 setup Plant #1
ADS1115 = 0x01  # 16-bit ADC
ads1115 = ADS1x15(ic=ADS1115, address=0x48)
gain = 6144  # +/- 6.144V # previously 4096  # +/- 4.096V
sps = 250  # Sample rate, Hz (ie samples per second)
try:
    # Determine if device present
    value = ads1115.readRaw(0, gain, sps)  # AIN0 wired to AirQuality Sensor
    config.ADS1115_Present = True
except TypeError as e:
    config.ADS1115_Present = False

# Setup Moisture Pin for GrovePowerSave
# TODO air quality too?
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(config.moisturePower, GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)
config.DEBUG = False

# Initialize Temp/Humidity sensor
hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()

# Sunlight SI1145 Sensor Setup
Sunlight_Sensor = SDL_Pi_SI1145.SDL_Pi_SI1145()

all_sensors = [
    "rangefinder",
    "airquality",
    "soilmoisture",
    "temperature",
    "humidity",
    "lumens",
    "ir",
    "uv",
]


def read_sensor(sensor):
    if sensor == "rangefinder":
        return ultrasonicRanger.measurementInCM()
    if sensor == "airquality":
        val = aq.readAirQualitySensor(ads1115)
        # interp = aq.interpretAirQualitySensor(val)
        return val
    if sensor == "soilmoisture":
        return extendedPlants.readExtendedMoistureExt(1, None, ads1115)
    if sensor == "temperature":
        return hdc1000.readTemperature()
    if sensor == "humidity":
        return hdc1000.readHumidity()
    if sensor == "lumens":
        return Sunlight_Sensor.readVisible()
    if sensor == "ir":
        return Sunlight_Sensor.readIR()
    if sensor == "uv":
        SunlightUV = Sunlight_Sensor.readUV()
        return SunlightUV / 100.0  # UV Index


conn = psycopg2.connect("postgresql://pi:smartgarden1@localhost/pi")
insert_sql = """
    INSERT INTO obs (
        time, airquality, humidity, ir, lumens, rangefinder, soilmoisture, temperature, uv, notes
    ) VALUES (
        %(time)s, %(airquality)s, %(humidity)s, %(ir)s, %(lumens)s, %(rangefinder)s, %(soilmoisture)s, %(temperature)s, %(uv)s, %(notes)s
    )
"""

while True:
    timestamp = datetime.utcnow()
    data = dict([(sensor, read_sensor(sensor)) for sensor in all_sensors])
    data["time"] = timestamp
    data["notes"] = None

    pprint(data)
    print

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, data)

    time.sleep(1.0)
