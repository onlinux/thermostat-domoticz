# Thermostat-Domoticz with Python and pygame

<img  src="/Images/Screenshot_20181229_155406.png" alt=" SVT Thermostat" />
<img  src="/Images/Screenshot_20181229_155153.png" alt=" SVT Thermostat Action screen" />
<img  src="/Images/Screenshot_20181229_155515.png" alt=" SVT Thermostat Forcast screen" />
<img  src="/Images/Screenshot_20181229_155611.png" alt=" SVT Thermostat Probe screen" />

# Installation libraries:

`git clone https://github.com/onlinux/thermostat-domoticz.git`
`cd thermostat-domoticz`

run:

 `$ sh setup.sh`

# Configuration

Modify config.ini

<pre>
[secret]
server= <enter your domoticz server name>
ip_domoticz=
port= <8080>
username= <username if exists>
password= <password to access your domoticz server>


# Start Thermostat Domoticz

`source venv/bin/activate`
`python z.py`

'Alt-PageDown' key or 'n' key to roll over the 4 available displays

Click to change Meteo Station when displaying forecasts.

Meteo Stations are defined within z.py

<pre>
tlocations = (
				{'code': 'FRXX0099' , 'color': BLACK},
				{'code': 'FRXX4269' , 'color': BLACK},
				{'code': 'FRXX3651' , 'color': BLACK},
				{'code': 'BRXX3505' , 'color': DARKGREEN}
)
