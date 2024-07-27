#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Date       : 24 April 2024 

import time as t
import json
import re, sys
import requests
import zoneinfo
from datetime import datetime,timedelta

wether_codes_config = './config/tomorrow_codes.json'
    
def readSettings(setting):
    tomorrow_io_config = './config/tomorrow_io_API_KEY.json'
    
    with open(tomorrow_io_config, 'r') as f:
        c = json.load(f)['tomorrow.io']
    f.close()
    
    setting['api_key'] = c['api_key']
    setting['api_version'] = c['version']
    setting['service'] = c['service']      
    setting['service_timesteps'] = ['1h', '1d']
    setting['service_fields'] = { '1h': ['temperature', 'humidity', 'windSpeed', 'windDirection','pressureSeaLevel', \
                                    'weatherCode','precipitationProbability','cloudCover', 'rainAccumulation', 'snowAccumulation', \
                                    ],
                            '1d': ['temperature', 'humidity', 'windSpeed', 'windDirection','pressureSeaLevel', \
                                    'sunriseTime','sunsetTime','weatherCodeFullDay','weatherCode','precipitationProbability', \
                                    'cloudCover', 'moonriseTime', 'moonsetTime', 'temperatureMax', 'temperatureMin', \
                                    'rainAccumulation', 'snowAccumulation']
                            }
    return setting

def zone_region(zone):
    tz_list = {
        'CET': 'Europe/Paris',
        'CST6CDT': 'America/Chicago',
        'Cuba': 'America/Havana',
        'EET': 'Europe/Sofia',
        'EST5EDT': 'America/New_York',
        'GB': 'Europe/London',
        'GB-Eire': 'Europe/London',
        'GMT': 'Etc/GMT',
        'Greenwich': 'Etc/GMT',
        'Hongkong': 'Asia/Hong_Kong',
        'HST': 'Pacific/Honolulu',
        'Iceland': 'Africa/Abidjan',
        'Iran': 'Asia/Tehran',
        'Israel': 'Asia/Jerusalem',
        'Jamaica': 'America/Jamaica',
        'Japan': 'Asia/Tokyo',
        'Kwajalein': 'Pacific/Kwajalein',
        'Libya': 'Africa/Tripoli',
        'MET': 'Europe/Paris',
        'MST': 'America/Phoenix',
        'Navajo': 'America/Denver',
        'NZ': 'Pacific/Auckland',
        'NZ-CHAT': 'Pacific/Chatham',
        'Poland': 'Europe/Warsaw',
        'Portugal': 'Europe/Lisbon',
        'PRC': 'Asia/Shanghai',
        'PST8PDT': 'America/Los_Angeles',
        'ROC': 'Asia/Taipei',
        'CST': 'Asia/Taipei',
        'ROK': 'Asia/Seoul',
        'Singapore': 'Asia/Singapore',
        'Turkey': 'Europe/Istanbul',
        'UCT': 'Etc/UTC',
        'Universal': 'Etc/UTC',
        'UTC': 'Etc/UTC',
        'W-SU': 'Europe/Moscow',
        'WET': 'Europe/Lisbon',
        'Zulu': 'Etc/UTC'
    }
    if zone in tz_list:
        return tz_list[zone]
    else:
        return zone

class TomorrowIo:
    icon = str()
    units = dict()
    direction = str()

    def __init__(self, config, api_data=None):
        s = str()
        self.now = int(t.time())
        self.config = readSettings(config)
        self.api_data = api_data
        zone = zone_region(self.config['timezone'])
        self.tz = zoneinfo.ZoneInfo(zone)
        #self.tz = zoneinfo.ZoneInfo(self.config['timezone'])
        tz_offset = self.tz.utcoffset(datetime.now())
        self.tz_offset = tz_offset.seconds if tz_offset.days == 0 else -tz_offset.seconds
        self.utc = zoneinfo.ZoneInfo('UTC')
        location = f'{self.config["lat"]},{self.config["lon"]}'
        fields = self.config['service_fields']
        self.url = f'https://api.tomorrow.io/{self.config["api_version"]}/timelines'

        with open(wether_codes_config, 'r') as f:
            tomorrow_codes = json.load(f)
        self.tomorrow_codes = tomorrow_codes
       
        if self.config['units'] == 'metric':
            self.units = {'pressure': 'hPa', 'wind_speed': 'm/s', 'temp': 'C'}
        elif self.config['units'] == 'imperial':
            self.units = {'pressure': 'inHg', 'wind_speed': 'mph', 'temp': 'F'}
        else:
            self.units = {'pressure': 'hPa', 'wind_speed': 'm/s', 'temp': 'K'}

    def ApiCall(self):
        location = f'{self.config["lat"]},{self.config["lon"]}'
        fields = self.config['service_fields']
        api_data = dict()
        for n in self.config['service_timesteps']:
            querystring = {
                "location":location,
                "fields":fields[n],
                "units":self.config['units'],
                "timesteps":n,
                'timezone': self.tz,
                "apikey":self.config['api_key']}

            r = requests.request("GET", self.url, params=querystring)
            if  r.ok:
                api_data[n] = r.json()
                t.sleep(1)
            else:
                print('API: Requests call rejected.')
                exit(1)    
        return api_data  

    def CurrentWeather(self):
        c = self.api_data['1h']['data']['timelines'][0]['intervals'][0]['values']
        s = self.api_data['1h']['data']['timelines'][0]['intervals'][0]['startTime']
        d = self.api_data['1d']['data']['timelines'][0]['intervals'][0]['values']
        # Time
        c['dt'] = self.conv_epoch(s)
        # Sunrise and Sunset
        c['sunrise'] = self.conv_epoch(d['sunriseTime']) if not d['sunriseTime'] == None else 0
        c['sunset'] = self.conv_epoch(d['sunsetTime']) if not d['sunsetTime'] == None else 0
        # daitime
        c['daytime'] = self.daytime(dt=datetime.now().timestamp(), sunrise=c['sunrise'], sunset=c['sunset'])
        #c['daytime'] = self.daytime(dt=c['dt'], sunrise=c['sunrise'], sunset=c['sunset'])
        c['darkmode'] = self.darkmode(config=self.config, daytime_state=c['daytime'])
        # Temperature
        c['temp'] = float(c['temperature'])
        # Pressure
        c['pressure'] = float(c['pressureSeaLevel'])
        # Clouds
        c['clouds'] = float(c['cloudCover'])
        # Wind speed and Cardinal direction
        c['wind_speed'] = float(c['windSpeed'])
        c['cardinal'] = self.cardinal(float(c['windDirection']))
        # Weather disc
        code_fullday = str(d['weatherCodeFullDay']) # int() to str() data
        _code_fullday = self.fix_weather(daytime=c['daytime'], code=code_fullday)
        c['description'] = self.tomorrow_codes['weatherCodeFullDay'][_code_fullday]
        # Main weather
        code_day = str(c['weatherCode']) # int() to str() data
        _code_day = self.fix_weather(daytime=c['daytime'], code=code_day) 
        w = self.tomorrow_codes["weatherCode"][_code_day]    
        c['main'] = self.fix_kindle_weather(w)
        # Add pop
        c['pop'] = round(float(c['precipitationProbability']) / 100,1)
        # Add 'in_clouds'
        if self.config['in_clouds'] == 'cloudCover':
            c['in_clouds'] = round(float(c['cloudCover']) / 100,1)
        elif self.config['in_clouds'] == 'probability':
            c['in_clouds'] = round(c['pop'],1) if 'pop' in c else 0
        else:
            c['in_clouds'] = 0
        return c

    def HourlyForecast(self, hour):
        h = self.api_data['1h']['data']['timelines'][0]['intervals'][hour]['values']
        s = self.api_data['1h']['data']['timelines'][0]['intervals'][hour]['startTime']
        d = self.api_data['1d']['data']['timelines'][0]['intervals'][0]['values']      
        # Time
        h['dt'] = self.conv_epoch(s)
        # Sunrise and Sunset
        h['sunrise'] = self.conv_epoch(d['sunriseTime']) if not d['sunriseTime'] == None else 0
        h['sunset'] = self.conv_epoch(d['sunsetTime']) if not d['sunsetTime'] == None else 0
        # daitime
        h['daytime'] = self.daytime(dt=h['dt'], sunrise=h['sunrise'], sunset=h['sunset'])
        # Temperature
        h['temp'] = float(h['temperature'])
        # Pressure
        h['pressure'] = float(h['pressureSeaLevel'])
        # Clouds
        h['clouds'] = float(h['cloudCover'])
        # Wind speed
        h['wind_speed'] = float(h['windSpeed'])
        # Cardinal direction
        h['cardinal'] = self.cardinal(float(h['windDirection']))
        # Main weather
        code_day = str(h['weatherCode']) # int() to str() data
        code_day = self.fix_weather(daytime=h['daytime'], code=code_day) 
        w = self.tomorrow_codes["weatherCode"][code_day]
        h['main'] = self.fix_kindle_weather(w)
        # Add pop
        h['pop'] = round(float(h['precipitationProbability']) / 100,1)
        # Add 'in_clouds'
        if self.config['in_clouds'] == 'cloudCover':
            h['in_clouds'] = round(float(h['cloudCover']) / 100,1)
        elif self.config['in_clouds'] == 'probability':
            h['in_clouds'] = round(h['pop'],1) if 'pop' in h else 0
        else:
            h['in_clouds'] = 0
        return h

    def DailyForecast(self, day):
        d = self.api_data['1d']['data']['timelines'][0]['intervals'][day]['values']
        s = self.api_data['1d']['data']['timelines'][0]['intervals'][day]['startTime']
        # Time
        d['dt'] = self.conv_epoch(s)
        # Sunrise and Sunset
        d['sunrise'] = self.conv_epoch(d['sunriseTime']) if not d['sunriseTime'] == None else 0
        d['sunset'] = self.conv_epoch(d['sunsetTime']) if not d['sunsetTime'] == None else 0
        # daitime
        d['daytime'] = self.daytime(dt=d['dt'], sunrise=d['sunrise'], sunset=d['sunset'])
        # Moonrise and Moonset
        d['moonrise'] = self.conv_epoch(d['moonriseTime']) if not d['moonriseTime'] == None else 0
        d['moonset'] = self.conv_epoch(d['moonsetTime']) if not d['moonsetTime'] == None else 0
        # Temperature
        d['temp_day'] = float(d['temperature'])
        d['temp_min'] = float(d['temperatureMin'])
        d['temp_max'] = float(d['temperatureMax'])
        # Pressure
        d['pressure'] = float(d['pressureSeaLevel'])
        # Clouds
        d['clouds'] = float(d['cloudCover'])
        # Wind speed
        d['wind_speed'] = float(d['windSpeed'])
        # Cardinal direction
        d['cardinal'] = self.cardinal(float(d['windDirection']))
        # Add pop
        d['pop'] = round(float(d['precipitationProbability']) / 100,1)
        # Add 'in_clouds'
        if self.config['in_clouds'] == 'cloudCover':
            d['in_clouds'] = round(float(d['cloudCover']) / 100,1)
        elif self.config['in_clouds'] == 'probability':
            d['in_clouds'] = round(d['pop'],1) if 'pop' in d else 0
        else:
            d['in_clouds'] = 0
        # Main weather
        code_day = str(d['weatherCode']) # int() to str()
        code_day = self.fix_weather(daytime=d['daytime'], code=code_day) 
        w = self.tomorrow_codes["weatherCode"][code_day]    
        d['main'] = self.fix_kindle_weather(w)
        return d

    def fix_weather(self, daytime, code):
        db = ('1000', '1100', '1101', '10000')
        if code in db:
            if  daytime == 'day' or daytime == 'midnight_sun':
                # Daytime
                code = code + 'd'
            else:
                # Night time
                code = code + 'n'
            return code
        else:
            return code

    def daytime(self, dt, sunrise, sunset):
        this_month = int(datetime.fromtimestamp(dt, self.tz).strftime("%m"))
        if not sunrise == 0:
            d = datetime.fromtimestamp(dt, self.tz)
            _dt = d.hour * 60 + d.minute
            d = datetime.fromtimestamp(sunrise, self.tz)
            _sunrise = d.hour * 60 + d.minute
            d = datetime.fromtimestamp(sunset, self.tz)
            _sunset = d.hour * 60 + d.minute
            if _dt > _sunrise and _dt < _sunset:
                state = 'day'
            else:
                state = 'night'
        else:
            # The other way: Northern hemisphere: From Sep to Feb is night-time, from March to Aug is daytime, sorthern hemisphere is the exact opposite.
            if float(self.config['lat']) < 0 and 3 < this_month <= 9:
                state = 'polar_night'
            elif float(self.config['lat']) < 0 and (0 < this_month <= 3 or 9 < this_month <= 12):
                state = 'midnight_sun'
            elif float(self.config['lat']) > 0 and 3 < this_month <= 9:
                state = 'midnight_sun'
            elif float(self.config['lat']) > 0 and (0 < this_month <= 3 or 9 < this_month <= 12):
                state = 'polar_night'
        return state
        
        
    def fix_kindle_weather(self, name):
        d = {
            'Sunny': 'ClearDay',
            'Clear Sky': 'ClearNight',
            'Mostly Clear Day': 'PartlyCloudyDay',
            'Mostly Clear Night': 'PartlyCloudyNight',
            'Partly Cloudy Day': 'PartlyCloudyDay',
            'Partly Cloudy Night': 'PartlyCloudyNight',
            'Mostly Cloudy': 'Cloudy',
            'Cloudy': 'Cloudy',
            'Fog': 'Fog',
            'Light Fog': 'Fog',
            'Drizzle': 'Drizzle',
            'Rain': 'Rain',
            'Light Rain': 'Rain',
            'Heavy Rain': 'Rain',
            'Snow': 'Snow',
            'Flurries': 'Wind',
            'Light Snow': 'Snow',
            'Heavy Snow': 'Snow',
            'Freezing Drizzle': 'Drizzle',
            'Freezing Rain': 'Rain',
            'Light Freezing Rain': 'Rain',
            'Heavy Freezing Rain': 'Rain',
            'Ice Pellets': 'Snow',
            'Heavy Ice Pellets': 'Snow',
            'Light Ice Pellets': 'Snow',
            'Thunderstorm': 'Thunderstorm'
        }
        return d[name]

    def cardinal(self, degree):
        if degree >= 348.75 or degree <= 33.75: return 'N'
        elif 33.75 <= degree <= 78.75: return 'NE'
        elif 78.75 <= degree <= 123.75: return 'E'
        elif 123.75 <= degree <= 168.75: return 'SE'
        elif 168.75 <= degree <= 213.75: return 'S'
        elif 213.75 <= degree <= 258.75: return 'SW'
        elif 258.75 <= degree <= 303.75: return 'W'
        elif 303.75 <= degree <= 348.75: return 'NW'
        else: return Noneq

    def conv_epoch(self, s):
        # python version
        v = sys.version_info.minor
        if not s == None:
            if v > 9:           
                a = datetime.fromisoformat(s)
            else:
                a = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
            return int(a.timestamp())
        else:
            return s

    def darkmode(self, config, daytime_state):
        if config['darkmode'] == True:
            darkmode = True
        elif config['darkmode'] == "Auto":
            if daytime_state == 'night' or daytime_state == 'polar_night':
                darkmode = True
            else:
                darkmode = False
        else:
            darkmode = False
        return darkmode

