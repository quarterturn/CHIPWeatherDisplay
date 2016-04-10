# CHIPWeatherDisplay

How to use:
1. git clone https://github.com/quarterturn/CHIPWeatherDisplay.git into /opt (or wherever)
2. edit PiTFTWeather.py and change weatherDotComLocationCode to your own location
3. edit /etc/rc.local and add '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start' before 'exit 0'
4. start the program: '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start'
5. throw something like this '0 5 * * * /usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py restart' in your root crontab to restart it each night, since I haven't figured out all the ways in which it will throw an exception yet.
