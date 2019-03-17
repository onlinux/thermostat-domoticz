# zibase-thermostat with Python and pygame

<img  src="/Images/Screenshot_20181229_155406.png" alt=" Zibase Thermostat" />
<img  src="/Images/Screenshot_20181229_155153.png" alt=" Zibase Thermostat Action screen" />
<img  src="/Images/Screenshot_20181229_155515.png" alt=" Zibase Thermostat Forcast screen" />
<img  src="/Images/Screenshot_20181229_155611.png" alt=" Zibase Thermostat Probe screen" />

# Installation libraries:

`git clone https://github.com/onlinux/zibase-thermostat.git`
`cd zibase-thermostat`

Install python-pip if not installed yet:
`sudo apt-get install python-pip`

Install pywapi from source
Download the latest pywapi library from: <https://launchpad.net/python-weather-api/trunk/0.3.8/+download/pywapi-0.3.8.tar.gz>

Untar the source distribution and run:

 `$ tar xvfz pywapi-0.3.8.tar.gz`

 `$ cd pywapi-0.3.8`

 `$ python setup.py build`

 `$ sudo python setup.py install`

 `$ cd ../zibase-thermostat/`

# Install pygame

 `$ sudo apt-get install python-pygame`

# Configuration

 <img  src="/Images/thermostat_variables.png" alt=" Zibase Thermostat variables" />

 Set [global] thermostat variables as specified within zibase interface

 Modify config.ini
 
 Referring to the screenshot, config.ini should look like this

 <pre>
 [secret]
 zibaseid = ZiBASE00xxxx
 tokenid  = 00xxxxxx
 [global]
 tempvariable= 28
 setpointdayvariable= 29
 setpointnightvariable= 30
 modevariable= 31
 statevariable= 13
 thermostatscenario= 32


# Start Thermostat Zibase

`python z.py`

Alt-PageDown key to roll over the 4 available displays

Click to change Meteo Station when displaying forecasts.

Meteo Stations are defined within z.py

<pre>
tlocations = (
				{'code': 'FRXX0099' , 'color': BLACK},
				{'code': 'FRXX4269' , 'color': BLACK},
				{'code': 'FRXX3651' , 'color': BLACK},
				{'code': 'BRXX3505' , 'color': DARKGREEN}
)
