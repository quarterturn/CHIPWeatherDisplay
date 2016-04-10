#!/usr/bin/env python

import sys
import os, syslog
import pygame
import time
from time import sleep, strftime
from datetime import datetime
import pywapi
import string

from daemon import Daemon

# Weather Icons used with the following permissions:
#
# VClouds Weather Icons
# Created and copyrighted by VClouds - http://vclouds.deviantart.com/
#
# The icons are free to use for Non-Commercial use, but If you use want to use it with your art please credit me and put a link leading back to the icons DA page - http://vclouds.deviantart.com/gallery/#/d2ynulp
#
# *** Not to be used for commercial use without permission! 
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***

installPath = "/opt/PiTFTWeather/"

# location for Raleigh, NC on weather.com
weatherDotComLocationCode = '27603:4:US'
# convert mph = kpd / kphToMph
kphToMph = 1.60934400061

# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

# update interval
updateRate = 600 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)

        os.putenv('SDL_FBDEV', '/dev/fb0')
        
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 3 sizes
font = pygame.font.Font(fontpath, 40)
fontSm = pygame.font.Font(fontpath, 30)
fontTime = pygame.font.Font(fontpath, 40)

# Inherit from daemon class
class Mydaemon(Daemon):
    # implement run method
    def run(self):
            # count minutes
            count = 0
            # compare when minute changes
            # set to something which will initially never match so display updates 1st time through loop
            tempMin = 60
            # also get the weather the first time through
            weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode,units = 'imperial')
            while True:
                if tempMin != datetime.now().strftime('%M'): 
                    # update tempMin
                    tempMin = datetime.now().strftime('%M')
                    # increment minute count
                    count = count + 1

                    # update weather every 5 minutes
                    if count == 5:
                        # reset the count
                        count = 0
                        # retrieve data from weather.com
                        weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode,units = 'imperial')
                    
                    # extract current data for today
                    try:
                        today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                            + weather_com_result['forecasts'][0]['date'][4:] + " " \
                            + weather_com_result['forecasts'][0]['date'][:3]
                    except ValueError:
                        break

                    windSpeed = weather_com_result['current_conditions']['wind']['speed']
                    if windSpeed == "calm":
                        windSpeed = '0'
                    currWind = windSpeed + " mph " + weather_com_result['current_conditions']['wind']['text']
                    currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "F"
                    # currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + " in"
                    currPress = weather_com_result['current_conditions']['barometer']['reading'] + " in"
                    uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
                    humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
                    
                    # extract forecast data
                    forecastDays = {}
                    forecaseHighs = {}
                    forecaseLows = {}
                    forecastPrecips = {}
                    forecastWinds = {}
                
                    start = 0
                    try:
                        test = float(weather_com_result['forecasts'][0]['day']['wind']['speed'])
                    except ValueError:
                        start = 1
                
                    for i in range(start, 5):
                    
                        if not(weather_com_result['forecasts'][i]):
                            break
                        forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
                        forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "F"
                        forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "F"
                        forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                        forecastWinds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])) + \
                            weather_com_result['forecasts'][i]['day']['wind']['text']
                        
                    # blank the screen
                    mytft.screen.fill(colourBlack)
                    
                    # Render the weather logo at 0,0
                    icon = installPath+ (weather_com_result['current_conditions']['icon']) + ".png"
                    logo = pygame.image.load(icon).convert()
                    mytft.screen.blit(logo, (0, 0))
                    
                    # set the anchor for the current weather data text
                    textAnchorX = 140
                    textAnchorY = 5
                    textYoffset = 40
                    
                    # add current weather data text artifacts to the screen
                    text_surface = font.render(today, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = font.render(currTemp, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = font.render(currWind, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = font.render(currPress, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = font.render(uv, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = font.render(humid, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                
                    # set X axis text anchor for the forecast text
                    textAnchorX = 0
                    textXoffset = 130
                    textYoffset = 30

                    
                    # add each days forecast text
                    for i in forecastDays:
                        textAnchorY = 260
                        text_surface = fontSm.render(forecastDays[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecaseHighs[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecaseLows[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecastPrecips[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecastWinds[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorX+=textXoffset
    
                    # set x axis text anchor for the time
                    textAnchorX = 420
                    textAnchorY = 5
                
                    # print the time
                    text_surface = fontTime.render(datetime.now().strftime('%H:%M'), True, colourWhite) 
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    # refresh the screen with all the changes
                    pygame.display.update()
                
        
if __name__ == "__main__":
    daemon = Mydaemon('/tmp/PiTFTWeather.pid', stdout='/tmp/PiTFTWeather.log', stderr='/tmp/PiTFTWeatherErr.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Starting")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Stopping")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Restarting")
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
