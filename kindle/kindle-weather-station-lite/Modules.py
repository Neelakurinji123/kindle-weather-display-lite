#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Date       : 24 April 2024 


import time as t
import sys, re, json, os, pathlib, io, math
from datetime import datetime, timedelta, date
import zoneinfo
import locale
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from SVGtools import circle, text, text2, fontfamily, transform, line, rect, path, spline
import Icons

if os.path.exists('./IconExtras.py'):
    import IconExtras as IconExtras
else:
    def IconExtras():
        return str()
        
def s_padding(x):
    if x >= 100 : return -5
    elif 100 > x >= 10 : return 10
    elif 10 > x >= 0 : return 30
    elif -10 < x < 0 : return 20
    elif x <= -10 : return 0

def read_i18n(p):
    filename = p.config['i18n_file']
    with open(filename, 'r') as f:
        try:
            a = json.load(f)['locale'][p.config['locale']]
        except:
            a = dict()
    return a
    
def split_text(wordwrap, text, max_rows):
    a, s = list(), list()
    d = dict()
    max_rows -= 1
    rows = 0
    if wordwrap == -1:
        return text
    for w in text.split():
        if len(''.join(s)) + len(w) + len(s) > wordwrap and rows < max_rows:
            d[rows] = s
            rows += 1
            s = [w]
            d[rows] = s
        elif len(''.join(s)) + len(w) + len(s) + 3 > wordwrap and rows == max_rows:
            s.append('...')
            d[rows] = s
            break
        else:
            s.append(w)
            d[rows] = s
    for n in d.values():
        a += [' '.join(n) + '\n']
    return a

def fix_text(w):
    w = re.sub(r'\&','&amp;', w)
    w = re.sub(r'\<','&lt;', w)
    w = re.sub(r'\>','&gt;', w)
    return w

def python_encoding(encoding):
    # convert Unix encoding to python encoding
    encoding_list={'us-ascii': 'ascii', 'iso-8859-1': 'latin_1', 'iso8859-1': 'latin_1', 'cp819': 'latin_1', \
                        'iso-8859-2': 'iso8859_2', 'iso-8859-4': 'iso8859_4', 'iso-8859-5': 'iso8859_5', \
                        'iso-8859-6': 'iso8859_6', 'iso-8859-7': 'iso8859_7', 'iso-8859-8': 'iso8859_8', \
                        'iso-8859-9': 'iso8859_9', 'iso-8859-10': 'iso8859_10', 'iso-8859-11': 'iso8859_11', \
                        'iso-8859-13': 'iso8859_13', 'iso-8859-14': 'iso8859_14', 'iso-8859-15': 'iso8859_15', \
                        'iso-8859-16': 'iso8859_16', 'utf8': 'utf_8'}
    return encoding_list[encoding]

def add_unit_temp(units, x, y, font_size):
    svg = str()
    if font_size == 50:
        svg += circle((x + 6), (y - 70), 6, 'black', 3, 'none').svg()
        svg += text('start', '35', (x + 15), (y  - 50), units['temp']).svg()
    elif font_size == 35:
        svg += circle((x + 5), (y - 23), 4, 'black', 2, 'none').svg()
        svg += text('start', '25', (x + 10), (y  - 10), units['temp']).svg()
    return svg

class Maintenant:
    def __init__(self, p, y):
        self.p = p
        self.config = p.config
        self.y = y
        self.font = self.p.config['font']
        
    def text(self):
        y = self.y + 40
        weather = self.p.CurrentWeather()
        daytime_state = weather['daytime']
        a = str()

        if weather['sunrise'] == 0:
            sunrise = "--:--"
        else:
            try:
                sunrise = str(datetime.fromtimestamp(weather['sunrise'], self.p.tz).strftime('%-H:%M'))
            except Exception as e:
                sunrise = '--:--'
        if weather['sunset'] == 0:
            sunset = '--:--'
        else:
            try:
                sunset = str(datetime.fromtimestamp(weather['sunset'], self.p.tz).strftime('%-H:%M'))
            except Exception as e:
                sunset = '--:--'
        # localtime
        maintenant = (str.lower(datetime.fromtimestamp(self.p.now, self.p.tz).strftime('%A, %d %B %-H:%M')))
        w = maintenant.split()
        #d = read_i18n(self.p)
        #w[0] = d["abbreviated_weekday"][w[0][:-1]] + ',' if not d == dict() else w[0]
        #w[2] = d["abbreviated_month"][w[2]] if not d == dict() else w[2]

        x_date = 20
        x_sunrise = x_date + 520
        x_sunset = x_sunrise + 125
        x_moon = 775
        r = 12      
        # moon icon
        d = weather['darkmode']
        if d == True:
            fg_color = 'rgb(255,255,255)'
            bg_color = 'rgb(0,0,0)'
        else:
            fg_color = 'rgb(0,0,0)'
            bg_color = 'rgb(255,255,255)'   
        a += circle(x_moon, (y - 10), (r - 1), fg_color, 0, fg_color).svg()    
        yr, mon, day, _, _, _, _, _, _ = datetime.now().timetuple()
        kw = {'p': self.p, 'day': day, 'mon': mon, 'yr': yr, 'lat': float(self.p.config['lat']), \
                'rx': x_moon, 'ry': (y - 10), 'r': r, 'ramadhan': self.p.config['ramadhan']}
        m = Moonphase(**kw)
        dm, ps, ram = m.calc()
        style = f'fill:{bg_color};stroke:{bg_color};stroke-width:0px;'
        a += m.svg(dm=dm, ps=ps, stroke_color=bg_color, r_plus=0, stroke=0, style=style)
        if m.darkmode == True and ps == 'f':
            color = 'rgb(0,0,0)'
            a += circle(x_moon, (y - 10), r, color, '2', color).svg()
                
        a += text('start', '30', x_sunrise, y, sunrise).svg()
        a += text('start', '30', x_sunset, y, sunset).svg()
        a += text('start', '30', x_date, y, ' '.join(w)).svg()
        svg = fontfamily(font=self.font, _svg=a).svg()
        return svg

    def icon(self):
        i = str()
        x_sunrise = 503
        x_sunset = x_sunrise + 127
        y_sun = self.y + 14
        i += transform(f'(1.1,0,0,1.1,{x_sunrise},{y_sun})', Icons.Sunrise()).svg()     
        i += transform(f'(1.1,0,0,1.1,{x_sunset},{y_sun})', Icons.Sunset()).svg()
        return i


class CurrentData:
    def precipitation(self):
        weather = self.p.CurrentWeather()
        a = str()           
        # 'in_clouds' option: cloudCover, probability
        if not self.p.config['in_clouds'] == str():
            #if weather['main'] in ['Rain', 'Drizzle', 'Snow', 'Sleet', 'Cloudy']:
            if weather['main'] in ['Cloudy']:
                v = Decimal(weather['in_clouds']).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
                padding = int(s_padding(v) * 0.64)
                if v == 0:
                    a += text('end', '45', (self.x_main + 230 - padding), (self.y_main + 215), "").svg()
                else:
                    if weather['main'] == self.sub_main:
                        font_size = '45'
                        x_main = self.x_main + 225
                        y_main = self.y_main + 247
                    else:
                        font_size = '40'
                        x_main = self.x_main + 185-20
                        y_main = self.y_main + 232

                    a += text('end', font_size, (x_main - padding), y_main, v).svg()
        return a

    def temperature(self):
        weather = self.p.CurrentWeather()
        daily = self.p.DailyForecast(0)
        style_line = 'stroke:black;stroke-width:1px;'
        a = str()
        # Temperature
        tempEntier = math.floor(weather['temp'])
        tempDecimale = 10 * (weather['temp'] - tempEntier)
        a += text('end', '100', (self.x_temp - 10), (self.y_temp), int(tempEntier)).svg()
        a += text('start', '50', (self.x_temp - 5), (self.y_temp - 5), '.' + str(int(tempDecimale))).svg()
        a += add_unit_temp(units=self.p.units, x=self.x_temp, y=self.y_temp, font_size=50)
        # Max temp
        a += text('end', '35', (self.x_temp + 113), (self.y_temp - 40), int(math.ceil(daily['temp_max']))).svg()
        a += add_unit_temp(units=self.p.units, x=(self.x_temp + 115), y=(self.y_temp - 40), font_size=35)
        # Line
        a += line((self.x_temp + 55), (self.x_temp + 155), (self.y_temp - 33), (self.y_temp - 33), style_line).svg()
        # Min temp
        a += text('end', '35', (self.x_temp + 113), (self.y_temp), int(math.ceil(daily['temp_min']))).svg()
        a += add_unit_temp(units=self.p.units, x=(self.x_temp + 115), y=self.y_temp, font_size=35)
        return a

    def pressure(self):
        weather = self.p.CurrentWeather()
        sp_x = -5
        if self.p.config['units'] == 'imperial':
            _sp = -10
        else:
            _sp = 0
        a = text('end', '30', (self.x_text + sp_x + 280 + _sp),(self.y_text + 360), str(round(weather['pressure']))).svg()
        a+= text('end', '23', (self.x_text + 320),(self.y_text + 360), self.p.units['pressure']).svg()
        return a

    def humidity(self):
        weather = self.p.CurrentWeather()
        x = self.x_text + 295
        x2 = self.x_text + 320
        y = self.y_text + 320
        a = text('end', '30', x, y, str(round(weather['humidity']))).svg()
        a += text('end', '23', x2, y, '%').svg()
        return a

    def wind(self):
        weather = self.p.CurrentWeather()
        weather['cardinal'] = str() if int(weather['wind_speed']) == 0 else weather['cardinal']
        x = self.x_text + 174
        x2 = self.x_text + 217
        y = self.y_text + 320
        if self.p.config['units'] == 'imperial':
            _sp = -10
        else:
            _sp = 0
        v = weather['cardinal'].lower() + ' ' + str(int(weather['wind_speed']))
        a = text('end', '30', (x + _sp), y, v).svg()
        a += text('end', '23', x2, y, self.p.units['wind_speed']).svg()
        return a

    def description(self):
        weather = self.p.CurrentWeather()
        y = self.y_text
        x = self.x_text
        a = str()
        self.wordwrap = 22
        disc = split_text(wordwrap=self.wordwrap, text=weather['description'].lower(), max_rows=2)
        for w in disc:
            a += text('end', '30', (x + 320), (y + 400), w).svg()
            y += 35
        return a

    def icon(self):
        weather = self.p.CurrentWeather()
        style_line = 'stroke:black;stroke-width:2px;'
        i = str()
        if weather['main'] == self.sub_main:
            y_main = self.y_main + 25
            return transform(f'(4,0,0,4,{self.x_main},{y_main})', addIcon(weather['main'])).svg()
        else:
            x_main = self.x_main - 5 - 20
            y_main = self.y_main + 40 
            x_sub_main = self.x_sub_main + 180
            y_sub_main = self.y_sub_main + 215
            i += line((x_main + 285), (x_main + 225), (y_main + 180), (y_main + 270), style_line).svg()
            i += transform(f'(3.5,0,0,3.5,{x_main},{y_main})', addIcon(weather['main'])).svg()   
            i += transform(f'(1.6,0,0,1.6,{x_sub_main},{y_sub_main})', addIcon(self.sub_main)).svg() 
            return i
            
class CurrentWeatherPane(CurrentData):
    def __init__(self, p, y=0, wordwrap=-1):
        self.p = p
        self.x = 0
        self.y = y
        self.wordwrap = wordwrap 
        self.x_main = self.x - 25
        self.y_main = y - 90
        self.x_sub_main = self.x
        self.y_sub_main = y - 90
        self.x_temp = self.x + 160
        self.y_temp = y + 305
        self.x_text = self.x
        self.y_text = y
        self.font = p.config['font']
        weather = p.CurrentWeather()
        self.day_state = weather['daytime']
        b = dict()
        # fix icons     
        for n in range(24):          
            weather = p.HourlyForecast(n)
            prob = 0.98
            prob **= n
            if self.day_state == 'night' or self.day_state == 'polar_night':
                if re.search('Day', weather['main']):
                    c = re.sub('Day', 'Night', weather['main'])
                else:
                    c = weather['main']
            else:
                if re.search('Night', weather['main']):
                    c = re.sub('Night', 'Day', weather['main'])
                else:
                    c = weather['main']
                    
            if c not in b:
                b[c] = 0
            b[c] += prob  
        self.sub_main = max(b.items(), key=lambda z: z[1])[0]
        
    def text(self):
        # genarate main info pane
        self.x_text = 260
        self.y_text = -125
        prec = super(CurrentWeatherPane, self).precipitation()
        self.x_temp = 415
        self.y_temp = 185
        temp = super(CurrentWeatherPane, self).temperature()
        self.x_text = 250
        self.y_text = -85
        pres = super(CurrentWeatherPane, self).pressure()
        self.x_text = 250
        humi = super(CurrentWeatherPane, self).humidity()
        self.x_text = 260
        wind = super(CurrentWeatherPane, self).wind()
        self.x_text = 250
        disc = super(CurrentWeatherPane, self).description()
        a = fontfamily(font=self.font, _svg=prec + temp + pres + humi + wind + disc).svg()
        return a


class HourlyWeatherPane:
    def __init__(self, p, y, hour, span, step, pitch):
        self.p = p
        self.y = y
        self.hour = hour
        self.span = span
        self.step = step
        self.pitch = pitch
        self.font = p.config['font']
        self.in_clouds = p.config['in_clouds']

    def text(self):
        y = self.y
        hrs = {3: 'three hours', 6: 'six hours', 9: 'nine hours'}
        d = read_i18n(self.p)
        a = str()
        # 3hr forecast
        x = 550
        for i in range(self.hour, self.span, self.step):
            weather = self.p.HourlyForecast(i)
            a += text('end', '35', (x + 200), (y + 90), round(weather['temp'])).svg()
            a += add_unit_temp(units=self.p.units, x=(x + 200), y=(y + 90), font_size=35)
            a += text('start', '30', (x + 55), (y + 160), hrs[i]).svg()
            # 'in_clouds' option: cloudCover, probability
            if not self.in_clouds == str():
                #if weather['main'] in ['Rain', 'Drizzle', 'Snow', 'Sleet', 'Cloudy']:
                if weather['main'] in ['Cloudy']:
                    v = Decimal(weather['in_clouds']).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
                    if v == 0:
                        a += text('end', '25', int(x + 160 - s_padding(v) * 0.357), (y + 82), '').svg()
                    else:
                        a += text('end', '25', int(x + 122 - s_padding(v) * 0.357), (y + 82), v).svg()
            y += self.pitch
        return fontfamily(font=self.font, _svg=a).svg()

    def icon(self):
        y = self.y
        i = str()
        c_weather = self.p.CurrentWeather()
        x = 550
        y += -30
        matrix = '2.0,0,0,2.0'
        for n in range(self.hour, self.span, self.step):
            weather = self.p.HourlyForecast(n)
            daytime_state = weather['daytime']
            # tweak weather icon
            if daytime_state == 'polar_night' and re.search('Day', weather['main']):
                weather['main'] = re.sub('Day', 'Night', weather['main'])
            elif daytime_state == 'midnight_sun' and re.search('Night', weather['main']):
                weather['main'] = re.sub('Night', 'Day', weather['main'])
            i += transform(f'({matrix},{x},{y})', addIcon(weather['main'])).svg()
            y += self.pitch
        return i

class GraphLabel:
    def __init__(self, p, y, s):
        self.p = p
        self.y = y 
        self.s = s
        self.w = p.config['w']
        self.label = p.config['graph_labels'][s]
        self.canvas = p.config['graph_canvas']
        self.canvas_w =  self.canvas['width']
        self.canvas_h = self.canvas['height']
        self.bgcolor = self.canvas['bgcolor']
        self.axis = self.canvas['axis']
        self.axis_color = self.canvas['axis_color']
        self.grid = self.canvas['grid']
        self.grid_color = self.canvas['grid_color']
        self.start = self.label['start']
        self.end = self.label['end']
        self.step = self.label['step']
        self.basis = self.label['basis']
        self.font_size = self.label['font-size']
        self.font = self.p.config['font']

    def text(self):
        a = str()
        if re.match('hourly', self.s):    
            a += GraphLabel.hourly(self)
        elif re.match('daily', self.s):    
            a += GraphLabel.daily(self)
        return a + '\n'
        
    def hourly(self):
        sp_x = int((self.w - self.canvas_w) * 0.5)
        box_size_x = self.canvas_w / (self.end - self.start)
        a = str()
        d = read_i18n(self.p)
        c = 0
        for n in range(self.start, self.end, self.step):
            weather = self.p.HourlyForecast(n)
            heure = datetime.fromtimestamp(weather['dt'], self.p.tz).strftime('%H')
            _x = int(sp_x + box_size_x * n + box_size_x * 0.5)
            if c % 3 == 1:
                heure = re.sub('^0', '', heure)
                a += text('middle', self.font_size, _x, (self.y + 4), str(heure)).svg()
            c += 1
        return fontfamily(font=self.font, _svg=a).svg()
            
    def daily(self):
        sp_x = int((self.w - self.canvas_w) * 0.5)
        box_size_x = self.canvas_w / (self.end - self.start)
        a = str()
        d = read_i18n(self.p)
        for n in range(self.start, self.end, self.step):
            weather = self.p.DailyForecast(n)
            jour = str.lower(datetime.fromtimestamp(weather['dt'], self.p.tz).strftime('%a'))
            jour = d['abbreviated_weekday'][jour] if not d == dict() else jour
            _x = int(sp_x + box_size_x * (n - self.start) + box_size_x * 0.5)
            a += text('middle', self.font_size, _x, (self.y + 4), str(jour)).svg()
        return fontfamily(font=self.font, _svg=a).svg()
 
class GraphLine:
    def __init__(self, p, y, obj):
        self.p = p
        self.y = y
        self.obj = obj
        self.start = self.obj['start']
        self.end = self.obj['end']
        self.stroke_color = self.obj['stroke-color']
        self.stroke_linecap = self.obj['stroke-linecap']
        self.stroke_width = self.obj['stroke-width']
        
    def draw(self): 
        style = f'stroke:{self.stroke_color};stroke-linecap:{self.stroke_linecap};stroke-width:{self.stroke_width}px;'
        i = line(x1=int(self.start), x2=int(self.end), y1=self.y, y2=self.y , style=style).svg()
        return i
        
class GraphPane:
    def __init__(self, p, y, obj):
        self.p = p
        self.y = y
        self.h = p.config['h']
        self.w = p.config['w']
        self.obj = obj
        self.type = self.obj['type']
        self.stroke = self.obj['stroke']
        self.stroke_color = self.obj['stroke-color']
        self.fill = self.obj['fill']
        self.stroke_linecap = self.obj['stroke-linecap']
        self.obj_w = self.obj['width'] if 'width' in self.obj else None
        self.start = self.obj['start']
        self.end = self.obj['end']
        self.step = self.obj['step']
        self.basis = self.obj['basis']
        self.title = self.obj['title']
        self.canvas = p.config['graph_canvas']
        self.canvas_w = self.canvas['width']
        self.canvas_h = self.canvas['height']
        self.bgcolor = self.canvas['bgcolor']
        self.axis = self.canvas['axis']
        self.axis_color = self.canvas['axis_color']
        self.grid = self.canvas['grid']
        self.grid_color = self.canvas['grid_color']
        self.grid_ext_upper = self.canvas['grid_ext_upper']
        self.grid_ext_lower= self.canvas['grid_ext_lower']
        self.style_bg = f'fill:{self.bgcolor};stroke:{self.bgcolor};stroke-width:0px;'
        self.style_axis = f'stroke:{self.axis_color};stroke-linecap:{self.stroke_linecap};stroke-width:1px;'
        self.style_grid = f'stroke:{self.grid_color};stroke-linecap:{self.stroke_linecap};stroke-width:{self.grid}px;'
        self.style_pline_fill = f'fill:{self.fill};stroke:{self.fill};stroke-width:0px;stroke-linecap:{self.stroke_linecap};'
        self.style_pline = f'fill:none;stroke:{self.stroke_color};stroke-width:{self.stroke}px;stroke-linecap:{self.stroke_linecap};'
        self.style_line = f'stroke:{self.stroke_color};stroke-linecap:{self.stroke_linecap};stroke-width:{self.stroke}px;'
        self.style_rect = f'fill:{self.fill};stroke:{self.stroke_color};stroke-linecap:{self.stroke_linecap};stroke-width:{self.stroke}px;'
        self.style_baseline = f'stroke:{self.axis_color};stroke-width:1px;'
        self.font = self.p.config['font']

    def draw(self):
        if self.type == 'spline':
            a = self.spline()
        elif self.type == 'bar':
            a = self.bar()
        elif self.type == 'rect':
            a = self.rect()
        elif self.type == 'tile':
            a = self.tile()
        return a

    def spline(self):
        y = self.y
        sp_x = int((self.w - self.canvas_w) * 0.5)
        box_size_x = self.canvas_w / self.end
        half_box = box_size_x * 0.5
        a = str()
        d = read_i18n(self.p)       
        # draw canvas
        a += rect(x=sp_x, y=(y - self.canvas_h + 140), width=self.canvas_w, height=(self.canvas_h - 45), style=self.style_bg).svg()
        # draw graph
        points = str()
        # get hourly temp graph data
        if self.basis == 'hour':
            # get max and min temp
            tMin = min([self.p.HourlyForecast(n)['temp'] for n in range(self.start, self.end, self.step)])
            tMax = max([self.p.HourlyForecast(n)['temp'] for n in range(self.start, self.end, self.step)])

            # get graph y-axis step
            tStep = 80 / (tMax - tMin) if (tMax - tMin) != 0 else 1
            # title
            title = f'{self.title}, 24 hours'
            a += text('start', '16', 5, (self.h - 5), title).svg()
            # computes temp x and y positions
            c = 0
            lst = list()
            for n in range(self.start, self.end, self.step):
                weather = self.p.HourlyForecast(n)
                x = int(sp_x + box_size_x * n + half_box)
                if n % 3 == 0 or n == (self.end - self.step):
                    _y = y - (weather['temp'] - tMin) * tStep + 75
                    lst.append((x, _y))
                # add temp every 3 steps
                if c % 3 == 0:    
                    a += text('middle', '25', x, (_y - 14), int(round(weather['temp']))).svg()
                    a += circle((x + 17), (_y - 29), 3, 'black', 2, 'none').svg()  
                c += 1
        # get daily temp graph data
        elif self.basis == 'day':
            # get max and min temp
            def temp(n):
                try:
                    return self.p.DailyForecast(n)['temp_day']
                except:
                    pass

            tMin = min([temp(n) for n in range(self.start, self.end, self.step) if temp(n) is not None])
            tMax = max([temp(n) for n in range(self.start, self.end, self.step) if temp(n) is not None])

            # get graph y-axis step
            tStep = 80 / (tMax - tMin) if (tMax - tMin) != 0 else 1
            # title
            title = f'{self.title}, {self.end} days'
            a += text('start', '16', 5, (self.p.config['h'] - 5), title).svg()
            # computes temp x and y positions
            lst = list()
            for n in range(self.start, self.end, self.step):
                try:
                    weather = self.p.DailyForecast(n)
                except IndexError:
                    break
                jour = str.lower(datetime.fromtimestamp(weather['dt'], self.p.tz).strftime('%a'))
                jour = d['abbreviated_weekday'][jour] if not d == dict() else jour
                x = int(sp_x + box_size_x * n + half_box)
                _y = y - (weather['temp_day'] - tMin) * tStep + 75
                lst.append((x, _y))
                # add temp
                a += text('middle', '25', x, (_y - 14), int(weather['temp_day'])).svg()
                a += circle((x + 17), (_y - 29), 3, 'black', 2, 'none').svg()              
        # draw filled graph
        a += spline(lst=lst, _x=lst[0][0], _y=(y + 95), stroke=self.fill, stroke_width=0, fill=self.fill).svg()
        # draw spline graph
        a += spline(lst=lst, stroke=self.stroke_color, stroke_width=self.stroke).svg()
        return fontfamily(font=self.font, _svg=a).svg()

    def bar(self):
        y = self.y
        sp_x = int((self.w - self.canvas_w) * 0.5)
        box_size_x = self.canvas_w / self.end
        a = str()
        i18n = read_i18n(self.p)
        # Canvas
        a += rect(x=sp_x, y=(y - self.canvas_h + 140), width=self.canvas_w, height=(self.canvas_h - 45), style=self.style_bg).svg()
        if self.basis == 'hour' and self.title == 'rain precipitation':
            # Graph
            th = 10.0 # threshold
            _min = min([self.p.HourlyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)])
            _max = max([self.p.HourlyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)])
            _sum = round(sum([self.p.HourlyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)]), 2)
            title = f'{self.title}, 24 hours'
            for n in range(self.start, self.end, self.step):
                weather = self.p.HourlyForecast(n)
                vol = weather['rainAccumulation']
                base_y = y - self.canvas_h + 290
                _vol = int((vol **(1/3)) * th)
                x = sp_x + int(box_size_x * n + box_size_x * 0.5)
                a += line(x1=x, x2=x, y1=base_y, y2=(base_y - _vol) , style=self.style_line).svg()
                if _max == vol and _max != 0:
                    a += text('middle', '16', x, (base_y - _vol - 10), f'{int(round(vol, 0))} mm').svg()
                    a += line(x, x, (base_y - _vol), (base_y - _vol - 8), self.style_axis).svg()
        elif self.basis == 'day' and self.title == 'rain precipitation':
            # Graph
            th = 5.75 # threshold
            _min = min([self.p.DailyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)])
            _max = max([self.p.DailyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)])
            _sum = round(sum([self.p.DailyForecast(n)['rainAccumulation'] for n in range(0, self.end, self.step)]), 2)
            title = f'{self.title}, {self.end} days'
            for n in range(self.start, self.end, self.step):
                try:
                    weather = self.p.DailyForecast(n)
                except IndexError:
                    break
                vol = weather['rainAccumulation']
                base_y = y - self.canvas_h + 290
                _vol = int((vol **(1/3)) * th)
                x = sp_x + int(box_size_x * n + box_size_x * 0.5)
                a += line(x1=x, x2=x, y1=base_y, y2=(base_y - _vol) , style=self.style_line).svg()
                if _max == vol and _max != 0:
                    a += text('middle', '16', x, (base_y - _vol - 12), f'{int(round(vol, 0))} mm').svg()
                    a += line(x, x, (base_y - _vol), (base_y - _vol - 10), self.style_axis).svg()
        # Baseline
        a += line(x1=sp_x, x2=(self.w - sp_x), y1=base_y, y2=base_y, style=self.style_baseline).svg()
        a += text('start', '16', 5, (self.h - 5), f'{title}, total: {int(round(_sum, 0))} mm').svg()
        return fontfamily(font=self.font, _svg=a).svg()

    def rect(self):
        y = self.y
        sp_x = int((self.p.config['w'] - self.canvas_w) * 0.5)
        box_size_x = self.canvas_w / self.end
        a = str()
        i18n = read_i18n(self.p)
        # Canvas
        a += rect(x=sp_x, y=(y - self.canvas_h + 140), width=self.canvas_w, height=(self.canvas_h - 45), style=self.style_bg).svg() 
        if self.basis == 'hour' and self.title == 'snow accumulation':
            # Graph
            th = 10.0 # threshold 
            _min = min([self.p.HourlyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)])
            _max = max([self.p.HourlyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)])
            _sum = round(sum([self.p.HourlyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)]), 2)
            title = f'{self.title}, 24hours'
            for n in range(self.start, self.end, self.step):
                weather = self.p.HourlyForecast(n)
                vol = weather['snowAccumulation']
                base_y = y - self.canvas_h + 290
                _vol = int(vol **(1/3) * th)
                _x = sp_x + int(box_size_x * n + box_size_x * 0.5)
                a += rect(x=_x - int(self.obj_w / 2), y=(base_y - _vol), width=self.obj_w , height=_vol , style=self.style_rect).svg()
                if _max == vol and _max != 0:
                    a += text('middle', '16', _x, (base_y - _vol - 12), f'{int(round(vol, 0))} mm').svg()
                    a += line(_x, _x, (base_y - _vol), (base_y - _vol - 10), self.style_axis).svg()

        elif self.basis == 'day' and self.title == 'snow accumulation':
            # Graph
            th = 5.75 # threshold  
            _min = min([self.p.DailyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)])
            _max = max([self.p.DailyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)])
            _sum = round(sum([self.p.DailyForecast(n)['snowAccumulation'] for n in range(0, self.end, self.step)]), 2) 
            title = f'{self.title}, {self.end} days'
            for n in range(0, self.end, self.step):
                try:
                    weather = self.p.DailyForecast(n)
                except IndexError:
                    break
                vol = weather['snowAccumulation']
                base_y = y - self.canvas_h + 290
                _vol = int(vol **(1/3) * th)
                _x = sp_x + int(box_size_x * n + box_size_x * 0.5)
                a += rect(x=_x - int(self.obj_w / 2), y=(base_y - _vol), width=self.obj_w , height=_vol , style=self.style_rect).svg()
                if _max == vol and _max != 0:
                    a += text('middle', '16', _x, (base_y - _vol - 12), f'{int(round(vol, 0))} mm').svg()
                    a += line(_x, _x, (base_y - _vol), (base_y - _vol - 10), self.style_axis).svg()
        # Baseline
        a += line(x1=(sp_x + 20), x2=(sp_x + self.canvas_w - 20), y1=base_y, y2=base_y, style=self.style_baseline).svg()
        # Text processing
        a += text('start', '16', 5, (self.h - 5), f'{title}, total: {int(round(_sum, 0))} mm').svg()
        return fontfamily(font=self.font, _svg=a).svg()

    def tile(self):
        sp_x = int((self.w - self.canvas_w) * 0.5)
        kwargs = {  'p': self.p, 'y': self.y, 'w': self.canvas_w, 'h': self.canvas_h, 'bgcolor': self.bgcolor, 'axis': self.axis, 
                    'axis_color': self.axis_color, 'grid': self.grid, 'grid_color': self.grid_color, 
                    'grid_ext_upper': self.grid_ext_upper, 'grid_ext_lower': self.grid_ext_lower, 
                    'title': self.title, 'start': self.start, 'step': self.step, 'end': self.end, 
                    'basis': self.basis, 'stroke': self.stroke, 
                    'stroke_color': self.stroke_color, 'fill': self.fill, 'stroke_linecap': self.stroke_linecap, 
                    'tz': self.p.tz, 'sp_x': sp_x}
        # Start
        a = str()
        # Canvas 
        a += rect(x=sp_x, y=(self.y - self.canvas_h + 140), width=self.canvas_w, height=(self.canvas_h - 45), style=self.style_bg).svg()

        def daily_weather(p, y, w, h, bgcolor, axis, axis_color, grid, grid_color, grid_ext_upper, grid_ext_lower, \
                            stroke, stroke_color, fill, stroke_linecap, \
                            title, start, end, step, basis, tz, sp_x, **kwargs):
            box_size_x = (w - (end - start - 1) * grid) / (end - start)
            half = int(box_size_x * 0.5)
            i18n = read_i18n(p)
            i, s = str(), str()
            c_weather = p.CurrentWeather()
            day_state = c_weather['daytime']
            for n in range(start, end, step):
                try:
                    weather = p.DailyForecast(n)
                except IndexError:
                    break
                jour = str.lower(datetime.fromtimestamp(weather['dt'], tz).strftime('%a'))
                #jour = i18n["abbreviated_weekday"][jour] if not i18n == dict() else jour
                # tweak weather icon
                if (day_state == 'polar_night' or day_state == 'night') and re.search('Day', weather['main']):
                    weather['main'] = re.sub('Day', 'Night', weather['main'])
                elif (day_state == 'midnight_sun' or day_state == 'day') and re.search('Night', weather['main']):
                    weather['main'] = re.sub('Night', 'Day', weather['main'])
                _x = int(sp_x + (box_size_x + grid) * (n - start))
                _y = y + 90

                i += transform(f'(1.8,0,0,1.8,{(_x - 10)},{(_y - 180)})', addIcon(weather['main'])).svg()
                s += text(anchor='end', fontsize='30', x=(_x + half - 20), y=_y, v=round(weather['temp_min']), stroke='rgb(128,128,128)').svg()
                s += circle((_x + half - 14), (_y - 20), 3, 'rgb(128,128,128)', 2, 'none').svg()
                s += text('end', '30', (_x + half + 45), _y, round(weather['temp_max'])).svg()
                s += circle((_x + half + 51), (_y - 20), 3, 'black', 2, 'none').svg()
                if n < (end - 1):
                    i += line((_x + box_size_x), (_x + box_size_x), (_y - h + 55 - grid_ext_upper), (_y + 5), self.style_grid).svg()

            return s,i

        def moon_phase(p, y, w, h, bgcolor, axis, axis_color, grid, grid_color, stroke, stroke_color, fill, stroke_linecap, \
                             grid_ext_upper, grid_ext_lower, title, start, end, step, basis, tz, sp_x, **kwargs):
            box_size_x = (w - (end - start - 1) * grid) / (end - start)
            half = int(box_size_x * 0.5)
            i18n = read_i18n(p)
            ramadhan = p.config['ramadhan']
            i, s = str(),str()
            for n in range(start, end, step):
                try:
                    weather = p.DailyForecast(n)
                except IndexError:
                    break
                jour = str.lower(datetime.fromtimestamp(weather['dt'], tz).strftime('%a'))
                jour = i18n["abbreviated_weekday"][jour] if not i18n == dict() else jour
                yr, mon, day, _, _, _, _, _, _ = datetime.fromtimestamp(weather['dt'], tz).timetuple()  
                lat = float(p.config['lat'])
                moonrise = '--:--' if weather['moonrise'] == 0 else str(datetime.fromtimestamp(weather['moonrise'], tz).strftime('%-H:%M'))
                moonset = '--:--' if weather['moonset'] == 0 else str(datetime.fromtimestamp(weather['moonset'], tz).strftime('%-H:%M'))                

                _x = int(sp_x + (box_size_x + grid) * n) 
                _y = y - 10
                # grid
                if n < (end - 1):
                    i += line((_x + box_size_x), (_x + box_size_x), (_y - h + 145 - grid_ext_upper), (_y + 105), self.style_grid).svg()                 
                # Moon icon
                r = 25
                kw = {'p': p, 'day': day, 'mon': mon, 'yr': yr, 'lat': lat, 'rx': _x + half, 'ry': _y + 15, 'r': r, 'ramadhan': ramadhan}
                m = Moonphase(**kw)
                dm, ps, ram = m.calc()
                style = f'fill:{fill};stroke:{stroke_color};stroke-width:1px;'
                i += m.svg(dm=dm, ps=ps, stroke_color=stroke_color, r_plus=2, stroke=stroke, style=style)
                if m.darkmode == True and ps == 'f':
                    i += circle(_x + half, _y + 15, r + 1, 'rgb(0,0,0)', '2', 'rgb(0,0,0)').svg()
                # Text: moonrise and moonset
                s += text('end', '20', (_x + box_size_x - 12), (_y + 95), moonrise).svg()
                s += text('start', '20', (_x + 12), (_y + 95), moonset, stroke='rgb(128,128,128)').svg()
                # Text: moon phase and ramadhan
                d = {'n': 'new', '1': 'first', 'f': 'full', '3': 'last'}
                ps = d[ps] if ps in d else str()
                ram = 'ram' if ram == 'r' else str()
                cap = ','.join(x for x in [ps, ram] if not x == str())
                s += text2('middle', 'bold', '18', (_x + half), (_y + 65), cap).svg()
    
            return s,i
        # Graph
        if self.basis == 'day' and self.title == 'weather':
            s,i = daily_weather(**kwargs)
        elif self.basis == 'day' and self.title == 'moon phase':
            s,i = moon_phase(**kwargs)        
            s += text('start', '16', 10, (self.h - 5), 'moon phase').svg()
        a += s + i         
        return fontfamily(font=self.font, _svg=a).svg()
 
class Moonphase:
    def __init__(self, **kw):
        self.p = kw.get('p')
        self.day = kw.get('day')
        self.mon = kw.get('mon')
        self.yr = kw.get('yr')
        self.lat = kw.get('lat')
        self.rx = kw.get('rx')
        self.ry = kw.get('ry')
        self.r = kw.get('r')
        self.ramadhan = kw.get('ramadhan')
        weather = self.p.CurrentWeather()
        self.daytime_state = weather['daytime']
        self.darkmode = weather['darkmode']
        
    def svg(self, dm, ps, stroke_color, r_plus, stroke, style):
        s = circle(self.rx, self.ry, (self.r + r_plus), stroke_color, stroke, "none").svg()
        s += path(dm, style).svg() if ps != 'f' else ''
        return s
        
    def calc(self):
        from hijridate import Hijri, Gregorian
        from astral import moon
        import math
        pi, cos, sin = math.pi, math.cos, math.sin
        
        def phase(rad):
            #one_day_step = 2 * pi / 56
            one_day_step = 2 * pi / 54
            if one_day_step > rad >= 0 or one_day_step > abs(pi * 2 - rad) >= 0:
                a = 'n'
            elif one_day_step > abs(rad - pi * 0.5) >= 0:
                a = '1'
            elif one_day_step > abs(rad - pi) >= 0:
                a = 'f'
            elif one_day_step > abs(rad - pi * 1.5) >= 0:
                a = '3'
            else:
                a = str()
            return a

        def moonphase(day, mon, yr):
            #g = Gregorian(yr, mon, day).to_hijri()
            #_, _, d = g.datetuple()
            #mooncycle = 29.55
            mooncycle = 27.99
            #a = d / mooncycle
            a = moon.phase(date(yr, mon, day)) / mooncycle
            return a

        def calc_ramadhan(day, mon, yr):
            g = Gregorian(yr, mon, day).to_hijri()
            if g.month_name() == 'Ramadhan':
                a = 'r'
            else:
                a = str()
            return a
            
        cairo_fix = True
        val = moonphase(self.day, self.mon, self.yr) # Astral v3.0 module: 0 <= val <= 1 
        rad = val * pi * 2 if val < 1 else pi * 2  
        ra1 = self.r
        ra2 = cos(rad) * self.r
        ra3 = self.r
        if self.lat > 0: # northern hemisphere
            if pi * 0.5 > rad >= 0:  # new moon to first quarter
                m = (pi * 0.5 - rad) / (pi * 0.5)
                flag1, flag2 = (1, 0) if self.darkmode == True else (0, 1)
                px1 = cos(pi * 0.5 + m) * self.r + self.rx
                py1 = sin(pi * 0.5 + m) * self.r + self.ry
                px2 = cos(pi * 0.5 + m) * self.r + self.rx
                py2 = -sin(pi * 0.5 + m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 1 {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            elif pi > rad >= pi * 0.5:  # first quarter to full moon
                if cairo_fix == True:
                    m = 0
                    flag1, flag2, flag3 = (0, 0, 1) if self.darkmode == True else (1, 1, 1)
                else:
                    m = (rad - pi * 0.5) / (pi * 0.5)
                    flag1, flag2, flag3 = (0, 0, 0) if self.darkmode == True else (1, 1, 0)
                px1 = cos(pi * 0.5 - m) * self.r + self.rx
                py1 = sin(pi * 0.5 - m) * self.r + self.ry
                px2 = cos(pi * 0.5 - m) * self.r + self.rx
                py2 = -sin(pi * 0.5 - m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 {flag3} {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            elif pi * 1.5 > rad >= pi:  # full moon to third quarter
                if cairo_fix == True:
                    m = 0
                    flag1, flag2, flag3 = (0, 0, 1) if self.darkmode == True else (1, 1, 1)
                else:
                    m = (pi * 1.5 - rad) / (pi * 0.5)
                    flag1, flag2, flag3 = (0, 0, 0) if self.darkmode == True else (1, 1, 0)
                px1 = cos(pi * 1.5 - m) * self.r + self.rx
                py1 = sin(pi * 1.5 - m) * self.r + self.ry
                px2 = cos(pi * 1.5 - m) * self.r + self.rx
                py2 = -sin(pi * 1.5 - m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 {flag3} {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            else:  # third quarter to new moon
                m = (rad - pi * 1.5) / (pi * 0.5)
                flag1, flag2 = (1, 0) if self.darkmode == True else (0, 1)
                px1 = cos(pi * 1.5 + m) * self.r + self.rx
                py1 = sin(pi * 1.5 + m) * self.r + self.ry
                px2 = cos(pi * 1.5 + m) * self.r + self.rx
                py2 = -sin(pi * 1.5 + m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 1 {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
        else: #southern hemisphere
            if pi * 0.5 > rad >= 0:  # new moon to first quarter
                m = (pi * 0.5 - rad) / (pi * 0.5)
                flag1, flag2 = (1, 0) if self.darkmode == True else (0, 1)
                px1 = cos(pi * 1.5 + m) * self.r + self.rx
                py1 = sin(pi * 1.5 + m) * self.r + self.ry
                px2 = cos(pi * 1.5 + m) * self.r + self.rx
                py2 = -sin(pi * 1.5 + m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 1 {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            elif pi > rad >= pi * 0.5:  # first quarter to full moon
                if cairo_fix == True:
                    m = 0
                    flag1, flag2, flag3 = (0, 0, 1) if self.darkmode == True else (1, 1, 1)
                else:
                    m = (rad - pi * 0.5) / (pi * 0.5)
                    flag1, flag2, flag3 = (0, 0, 0) if self.darkmode == True else (1, 1, 0)
                px1 = cos(pi * 1.5 - m) * self.r + self.rx
                py1 = sin(pi * 1.5 - m) * self.r + self.ry
                px2 = cos(pi * 1.5 - m) * self.r + self.rx
                py2 = -sin(pi * 1.5 - m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 {flag3} {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            elif pi * 1.5 > rad >= pi:  # full moon to third quarter
                if cairo_fix == True:
                    m = 0
                    flag1, flag2, flag3 = (0, 0, 1) if self.darkmode == True else (1, 1, 1)
                else:
                    m = (pi * 1.5 - rad) / (pi * 0.5)
                    flag1, flag2, flag3 = (0, 0, 0) if self.darkmode == True else (1, 1, 0)
                px1 = cos(pi * 0.5 - m) * self.r + self.rx
                py1 = sin(pi * 0.5 - m) * self.r + self.ry
                px2 = cos(pi * 0.5 - m) * self.r + self.rx
                py2 = -sin(pi * 0.5 - m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 {flag3} {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
            else:  # third quarter to new moon
                m = (rad - pi * 1.5) / (pi * 0.5)
                flag1, flag2 = (1, 0) if self.darkmode == True else (0, 1)
                px1 = cos(pi * 0.5 + m) * self.r + self.rx
                py1 = sin(pi * 0.5 + m) * self.r + self.ry
                px2 = cos(pi * 0.5 + m) * self.r + self.rx
                py2 = -sin(pi * 0.5 + m) * self.r + self.ry
                dm = f'M{px1} {py1} A{ra1} {ra1} 0 {flag1} {flag2} {px2} {py2} {ra2*0.98} {ra3*0.98} 0 1 1 {px1} {py1}z'
                ps = phase(rad)
                ram = calc_ramadhan(self.day, self.mon, self.yr) if self.ramadhan == True else str()
        return dm, ps, ram

def addIcon(s):
    if s == 'ClearDay':
        if ("ClearDay" in dir(IconExtras)) == True: return IconExtras.ClearDay()
        else: return Icons.ClearDay()
    elif s == 'ClearNight':
        if ("ClearNight" in dir(IconExtras)) == True: return IconExtras.ClearNight()
        else: return Icons.ClearNight()
    elif s == 'Rain':
        if ("Rain" in dir(IconExtras)) == True: return IconExtras.Rain()
        else: return Icons.Rain()
    elif s == 'Drizzle':
        if ("Drizzle" in dir(IconExtras)) == True: return IconExtras.Drizzle()
        else: return Icons.Rain()
    elif s == 'Thunderstorm':
        if ("Thunderstorm" in dir(IconExtras)) == True: return IconExtras.Thunderstorm()
        else: return Icons.Rain()
    elif s == 'Snow':
        if ("Snow" in dir(IconExtras)) == True: return IconExtras.Snow()
        else: return Icons.Snow()
    elif s == 'Sleet':
        if ("Sleet" in dir(IconExtras)) == True: return IconExtras.Sleet()
        else: return Icons.Snow()
    elif s == 'Wind':
        if ("Wind" in dir(IconExtras)) == True: return IconExtras.Wind()
        else: return Icons.Wind()
    elif s == 'Cloudy':
        if ("Cloudy" in dir(IconExtras)) == True: return IconExtras.Cloudy()
        else: return Icons.Cloudy()
    elif s == 'PartlyCloudyDay':
        if ("PartlyCloudyDay" in dir(IconExtras)) == True: return IconExtras.PartlyCloudyDay()
        else: return Icons.PartlyCloudyDay()
    elif s == 'PartlyCloudyNight':
        if ("PartlyCloudyNight" in dir(IconExtras)) == True: return IconExtras.PartlyCloudyNight()
        else: return Icons.PartlyCloudyNight()
    elif s == 'Mist':
        if ("Mist" in dir(IconExtras)) == True: return IconExtras.Mist()
        else: return Icons.Fog()
    elif s == 'Smoke':
        if ("Smoke" in dir(IconExtras)) == True: return IconExtras.Smoke()
        else: return Icons.Fog()
    elif s == 'Haze':
        if ("Haze" in dir(IconExtras)) == True: return IconExtras.Haze()
        else: return Icons.Fog()
    elif s == 'Dust':
        if ("Dust" in dir(IconExtras)) == True: return IconExtras.Dust()
        else: return Icons.Fog()
    elif s == 'Fog':
        if ("Fog" in dir(IconExtras)) == True: return IconExtras.Fog()
        else: return Icons.Fog()
    elif s == 'Sand':
        if ("Sand" in dir(IconExtras)) == True: return IconExtras.Sand()
        else: return Icons.Fog_icon()
    elif s == 'Dust':
        if ("Dust" in dir(IconExtras)) == True: return IconExtras.Dust()
        else: return Icons.Fog()
    elif s == 'Ash':
        if ("Ash" in dir(IconExtras)) == True: return IconExtras.Ash()
        else: return Icons.Fog()
    elif s == 'Squall':
        if ("Squall" in dir(IconExtras)) == True: return IconExtras.Squall()
        else: return Icons.Rain()
    elif s == 'Tornado':
        if ("Tornado" in dir(IconExtras)) == True: return IconExtras.Tornado()
        else: return Icons.Wind()
    elif s == 'Cyclone':
        if ("Cyclone" in dir(IconExtras)) == True: return IconExtras.Cyclone()
        else: return Icons.Wind()
    elif s == 'Snow2':
        if ("gSnow2" in dir(IconExtras)) == True: return IconExtras.Snow2()
        else: return Icons.Snow()
    else:
        return None

