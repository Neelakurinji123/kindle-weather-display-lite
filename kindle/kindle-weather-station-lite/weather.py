#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Update     : 8 May 2024


import time as t
import sys, re, json, io, os
from pathlib import Path
import zoneinfo
import locale
import shutil
from subprocess import Popen, PIPE
from wand.image import Image
from wand.display import display
from cairosvg import svg2png
from Modules import Maintenant, CurrentWeatherPane, HourlyWeatherPane, GraphPane, GraphLabel, GraphLine
import SVGtools

# Working dir
this_file = os.path.realpath(__file__)
path = str(Path(this_file).parents[0])
os.chdir(path)

svgfile = "/tmp/KindleStation.svg"
pngfile = "/tmp/KindleStation.png"
flatten_pngfile = "/tmp/KindleStation_flatten.png"
error_image = "./img/error_service_unavailable.png"
i18n_config = "./config/i18n.json"
graph_config = './config/graph_config.json'

def svg_processing(p, text=str(), draw=str(), y=0):
    graph_objects = p.config['graph_objects']
    for s in p.config['layout']:
        if s == 'maintenant':
            a = Maintenant(p=p, y=y)
            text += a.text()
            draw += a.icon()
            y += 50
            #y += 40
        elif s == 'main':
            wordwrap = 18
            a = CurrentWeatherPane(p=p, y=y, wordwrap=wordwrap)
            text += a.text()
            draw += a.icon()
            start_hour, span, step, pitch = 3, 9, 3, 155
            a = HourlyWeatherPane(p=p, y=y, hour=start_hour, span=span, step=step, pitch=pitch)
            text += a.text()
            draw += a.icon()
            y += 340
        elif s == 'graph':
            obj = graph_objects.pop(0)
            a = GraphPane(p=p, y=y+40, obj=obj)
            draw += a.draw()
            y += 120
        elif re.search('xlabel', s):
            a = GraphLabel(p=p, y=y+25, s=s)
            text += a.text()
            y += 40
        elif re.match(r'(padding[\+\-0-9]*)', s):
            y += int(re.sub('padding', '', s))
        elif re.search('h_line', s):
            a = GraphLine(p=p, y=y, obj=p.config['graph_lines'][s])
            draw += a.draw()
    return text, draw

def img_processing(p, svg):
    w = p.config['w']
    h = p.config['h']
    weather = p.CurrentWeather()
    darkmode = weather['darkmode']
    b_png = io.BytesIO()
    svg2png(bytestring=svg, write_to=b_png, background_color="white", parent_width=w, parent_height=h)
    png_val = b_png.getvalue()
    if darkmode == True:
        with Image(blob=png_val) as img:
            img.negate(True,"all_channels")
            img.format = 'png'
            img_blob = img.make_blob('png')
        img.close()
        png_val = img_blob

    with Image(blob=png_val) as img:
        img.rotate(90)
        img.alpha_channel_types = 'flatten'
        img.save(filename=flatten_pngfile)
    img.close()

def main(config, flag_dump, flag_config, flag_svg, flag_png):    

    try:
        if config['api'] == 'Tomorrow.io':
            from TomorrowIoAPI import TomorrowIo

            #test
            #with open(f'{path}/Tomorrow.io_API_output.json', 'r') as f:
            #    api_data = json.load(f)

            api_data = TomorrowIo(config=config).ApiCall()
            if not flag_dump == True:
                p = TomorrowIo(config=config, api_data=api_data)

        ## test: API data dump ##
        if flag_dump == True:
            output = f'{path}/{config["api"]}_API_output.json'
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(api_data, f, ensure_ascii=False, indent=4)
                exit(0)
        elif flag_config == True:
            print(json.dumps(p.config, ensure_ascii=False, indent=4))
            exit(0)

        # get Kindle's display size
        try:
            with open("/sys/class/graphics/fb0/virtual_size", 'r') as f:
                s = f.readline().strip()
                kindle_h, kindle_w = s.split(',')
        except:
            if p.config['kindle_w'] == None and p.config['kindle_h'] == None:
                kindle_h, kindle_w = 600, 800
            else:
                kindle_h = p.config['kindle_h']
                kindle_w = p.config['kindle_w']

        # main body
        text, draw = svg_processing(p=p)
        # add footer
        s = f'{p.config["city"]} - {p.config["api"]} API'
        _s = SVGtools.text('end', '16', (p.config['w'] - 5), (p.config['h'] - 5), s).svg()
        text += SVGtools.fontfamily(font=p.config['font'], _svg=_s).svg()
        _svg = text + draw
        svg =  SVGtools.format(encoding=p.config['encoding'], height=kindle_h, width=kindle_w, font=p.config['font'], _svg=_svg).svg()
        if flag_svg == True:
            output = svgfile
            with open(output, 'w', encoding='utf-8') as f:
                f.write(svg)
            f.close()    
            exit(0)
        else:
            img_processing(p=p, svg=svg)

    except Exception as e:
        print(e)
        shutil.copyfile(error_image, flatten_pngfile)
        exit(1)

    if flag_png == True:
        exit(0)

    # Display on kindle
    if os.uname().nodename == 'kindle':
        if os.environ.get('KINDLE_VER') == 'k3':
            cmd = './initialize_k3.sh'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()
            cmd = '/usr/sbin/eips -c'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()
            cmd = f'cd /tmp; /usr/sbin/eips -g {flatten_pngfile}'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()
        else:
            cmd = './initialize_pw1.sh'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()
            cmd = '/usr/sbin/eips -c -f'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()
            cmd = f'cd /tmp; /usr/sbin/eips -g {flatten_pngfile}'
            out = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE).wait()

if __name__ == "__main__":
    flag_dump, flag_config, flag_svg, flag_png = False, False, False, False
    if 'dump' in sys.argv:
        flag_dump = True
        sys.argv.remove('dump')
    elif 'config' in sys.argv:
        flag_config = True
        sys.argv.remove('config')
    elif 'svg' in sys.argv:
        flag_svg = True
        sys.argv.remove('svg')
    elif 'png' in sys.argv:
        flag_png = True
        sys.argv.remove('png')

    # Use custom setting
    if len(sys.argv) > 1:
        setting = sys.argv[1]
    else:
        setting = "setting.json" # Default setting

    with open(setting, 'r') as f:
        service = json.load(f)['station']
    f.close()
    
    config = dict()
    config['city'] = service['city'] if 'city' in service else None
    config['timezone'] = service['timezone'] if 'timezone' in service else None
    config['locale'] = service['locale'] if 'locale' in service else 'en_US.UTF-8'
    config['encoding'] = service['encoding'] if 'encoding' in service else 'iso-8859-1'
    config['font'] = service['font'] if 'font' in service else 'Droid Sans'
    config['darkmode'] = service['darkmode'] if 'darkmode' in service else False
    config['api'] = service['api']
    config['lat'] = str(service['lat'])
    config['lon'] = str(service['lon'])
    config['units'] = service['units'] if 'units' in service else 'metric'
    config['lang'] = service['lang'] if 'lang' in service else 'en'
    config['in_clouds'] = service['in_clouds'] if 'in_clouds' in service else str()  # Options: "cloudCover", "probability"
    config['layout'] = service['layout']
    config['w'], config['h'] = 800, 600   
    config['ramadhan'] = service['ramadhan']
    config['i18n_file'] = i18n_config

    with open(graph_config, 'r') as f:
        graph = json.load(f)['graph']
    f.close()
    
    config['graph_lines'] = graph['lines']
    config['graph_labels'] = graph['labels']
    b = list(service['graph_objects']) if 'graph_objects' in service else None
    if not b == None:
        config['graph_canvas'] = graph['canvas'][service['graph_canvas']]
        config['graph_objects'] = list()
        for n in b:
            config['graph_objects'].append(graph['objects'][n])           
    else:
        config['graph_canvas'] = dict()
        config['graph_objects'] = list()
        
    if 'kindle' in graph:
        config['kindle_w'] = graph['kindle']['w']
        config['kindle_h'] = graph['kindle']['h']
    else:
        config['kindle_w'] = None
        config['kindle_h'] = None

    main(config, flag_dump, flag_config, flag_svg, flag_png)
    

