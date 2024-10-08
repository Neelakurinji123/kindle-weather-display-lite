# Kindle Weather Display lite

This program is for a weather display on old Kindle 3 and Paperwhite 1 based on the original work by [Kindle-weather-station](https://gitlab.com/iero/Kindle-weather-station)

## Weather API

Following API is available:

- [Tomorrow.io](https://www.tomorrow.io/) (Free Tier)
  - hourly & daily for next 5 days
 
## Screenshots

<kbd><img src="sample_screenshots/screenshot1.jpg" height="360" alt="Kindle 3 Screenshot" /></kbd>&nbsp;

<kbd><img src="sample_screenshots/KindleStation_flatten.png" height="360" alt="Kindle 3 Screenshot" /></kbd>&nbsp;

## Requirements

- Jailbroken Kindle: https://wiki.mobileread.com/wiki/Kindle\_Hacks\_Information

## Set up server

### 1. Install the program

Copy `(github)/kindle/kindle-weather-station` to `(kindle)/mnt/us/kindle-weather-station-lite`.

### 2. Set up user account

In config directory, edit `tomorrow_io_API_KEY.json`

### 3. Edit config files

Tempalate's names are `setting_*.json`.

Default config is `setting.json`.


### 4. Install Graphics converters, Python3 and modules.

#### Applications

- imageMagick (include in pythgon3 packgage)
- cairo (system) and cairosvg

#### Python3(v3.11 or newer) and module Requirements

- tzdata
- requests
- setuptools
- pip
- Wand
- cairosvg
- hijridate (optional, for moon\_phase module)



### 5. Network Time Synchronization

To retrieve data correctly, setup NTP server.

### 6. Test run

All set up finished, then try it.

`. ./env_pw1; ./weather.py png` # use default config

or one of config files:

`. ./env_pw1; ./weather.py setting_######.json png`

Take a look at `/tmp/KindleStation_flatten.png`.


### 7. USB network

PW1:

```
                [LOCAL NETWORK]               			                                   [Wi-Fi]
                e.g.(192.168.1.0/24).        192.168.1.XX/24(wifi)
 WAN <-> ROUTER <--------------> PC <------> KINDLE
                          192.168.15.1/24    192.168.15.244/24(fix)
		                                      [USB NETWORK]                                             
```

When usbnet setup was finished, enable sshd server in KUAL, access to Kindle. 

```
ssh root@192.168.15.244
```

### 8. Setup ssh Auth key (optional)

- Create the server's pubkey.
- Set up the server's ssh client environment.
- Copy the server's ssh pubkey to Kindle.

e.g.) dropbear (openwrt)

```
cd /etc/dropbear
dropbearkey -y -f dropbear_rsa_host_key | grep "^ssh-rsa " > dropbear_rsa_host_key.pub
mkdir /root/.ssh
cd /root/.ssh
ln -s /etc/dropbear/dropbear_rsa_host_key id_dropbear
cd -
scp dropbear_rsa_host_key.pub root@192.168.2.2:/tmp
ssh root@192.168.15.244  # access to Kindle
cat /tmp/dropbear_rsa_host_key.pub >> /mnt/us/usbnet/etc/authorized_keys
exit
ssh root@192.168.15.244  # test passwordless login
```

e.g.) openssh (openwrt)

```
cd /root/.ssh
opkg update
opkg install openssh-client openssh-keygen openssh-sftp-client
ssh-keygen -t rsa
scp id.pub root@192.168.2.2:/tmp
ssh root@192.168.15.244  # access to Kindle
cat /tmp/id.pub >> /mnt/us/usbnet/etc/authorized_keys
exit
ssh root@192.168.15.244  # test passwordless login
```

### 9. Test run

```
cd /mnt/us/kindle-weather-station-lite
. ./env_pw1
./weather.py [config file]
```

## Layout
Layout size is 600 x 800.
The program's layout is as follows:

| Module name       | Function                   | Size (Y-axis) |
|:------------------|:---------------------------|--------------:|
| maintenant        | Time information           | 40            |
| main              | Current and hourly weather | 480           |
| graph             | Graph  or tile             | 120           |
| daily_xlabel_landscape4 | Label on daily weather from next day  | 20            |
| daily_xlabel_landscape5_start0 | Label on hourly weather from today | 20        |
| hourly_xlabel_landscape_start0 | Label on hourly weather from today | 20    |
| padding[-+0-9]*   | Insert spaces (Y axis only)|               |


### 1. maintenant

<kbd><img src="sample_screenshots/readme_imgs/maintenant.png" /></kbd>&nbsp;

- date
- sunrise
- sunset
- moonphase

### 2. main

<kbd><img src="sample_screenshots/readme_imgs/main_pane.png" /></kbd>&nbsp;

- config
  - "timezone": "Pacific/Auckland" # UNIX zoneinfo
  - "encoding": "iso-8859-1"  # encoding name
  - "locale": "en_US.UTF-8"  # locale name
  - "lat": "-77.8400829"  # latitude
  - "lon": "166.6445298"  # longitude
  - "units": "metric" # options: metric, imperial
  - "lang": "en" # language: en (English)
  - "darkmode": true, false and "Auto"
  
#### 2.1 Value in cloud icon

<kbd><img src="sample_screenshots/readme_imgs/inside_clouds.png" /></kbd>&nbsp;

- config
  - "in_clouds". : Value from 0 to 1.0 (0% to 100%)
     - "probability" : Probability of precipitation
     - "cloudCover" : Cloud thickness
     - "(empty)" : None

     
### 3. graph and tile

Available options are as follows:

- config: "graph\_objects"
  - "daily\_temperature\_spline\_landscape5": Daily Temperature
  - "daily\_rain\_precipitation\_5cols": Daily Rain Precipitation
  - "daily\_snow\_accumulation\_5cols": Daily Snow Accumulation
  - "daily\_weather\_landscape4": Daily Weather
  - "hourly\_temperature\_spline\_landscape": Hourly Temperature
  - "hourly\_rain\_precipitation": Hourly Rain Precipitation
  - "hourly\_snow\_accumulation": Hourly Snow Accumulation 
  - "moon\_phase\_landscape5": Moon Phase



#### 3.1 Daily Temperature

<kbd><img src="sample_screenshots/readme_imgs/KindleStation_spline.png" /></kbd>&nbsp;

- config
  - "graph\_objects": ["daily\_temperature\_spline\_landscape5"]

    

#### 3.2 Moon Phase

<kbd><img src="sample_screenshots/readme_imgs/moonohase.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "moon\_phase\_landscape5"]
  - "ramadhan": "True"

#### 3.3 Hourly Precipitation

<kbd><img src="sample_screenshots/readme_imgs/hourly_rain.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "hourly\_precipitation"]

#### 3.4 daily Precipitation

<kbd><img src="sample_screenshots/readme_imgs/daily_rain.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "daily\_rain\_precipitation\_5cols"]

  
#### 3.5 daily weather

<kbd><img src="sample_screenshots/readme_imgs/weather_tile.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "daily\_weather\_landscape4"]


#### 3.6 hourly snow accumulation

<kbd><img src="sample_screenshots/readme_imgs/hourly_snow.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "hourly\_snow\_accumulation"]


#### 3.7 daily snow accumulation

<kbd><img src="sample_screenshots/readme_imgs/daily_snow.png" /></kbd>&nbsp;

- config
  - "graph\_objects": [ "daily\_snow\_accumulation\_5cols"]

    
## Setting up time schedule

Edit crontab and restart cron.

e.g. for pw1)

`/etc/crontab/root`

```
0 */2 * * * sh -c "cd /mnt/us/kindle-weather-station-lite; . ./env_pw1; ./weather.py 2>>/tmp/kindle-weather-station.err"
0 1,3,5,7,9,11,13,15,17,19,21,23 * * * sh -c "cd /mnt/us/weather-station-lite; . ./env_pw1; ./kindle-weather.py 2>>/tmp/kindle-weather-station.err"
```

restart cron

```
kill -HUP `pidof crond`
```

# Credits

- [Tomorrow.io](https://www.tomorrow.io/) , Weather API
- [Bézier curves formula](https://www.particleincell.com/2012/bezier-splines/)