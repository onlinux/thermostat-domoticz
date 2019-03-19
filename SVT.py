#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2019
# http://blog.onlinux.fr
#
# Smart Virtual Thermostat python plugin for Domoticz is provided
# by Logread. Many thanks to him!
# SVT Domoticz repository : https://github.com/999LV/SmartVirtualThermostat.git
#
# Import required Python libraries
import time
import logging
import json
#import urllib.parse as parse
import urllib2 as request
import base64
import urllib
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s:%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class Constants:
    mode = {
        # Important! do not set 0  as 'stop' otherwise it will
        # override control 'stop' mode and it won't stop the thermostat!
        0: 'Off',
        10: 'jour',
        20: 'nuit'
    }

    control = {
        0: 'stop',
        10: 'automatique',
        20: 'forcé'
    }

    switchState = {
        # Important! case sensitive On and Off for switch
        0: 'Off',
        1: 'On'
    }


class SVT(object):
    'Common base class for SVT'

    modeDict = {
        0: 'automatique',
        1: 'stop',
        2: 'jour',
        3: 'nuit',
        4: 'forcé'
    }

    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.switchId = None
        self.indoorProbeId = None
        self.outdoorProbeId = None
        self.stateId = None
        self.modeId = None
        self.controlId = None
        self.setpointNormalId = None
        self.setpointEconomyId = None
        self.indoorTempId = None
        self.outdoorTempId = None
        self.username = username
        self.password = password
        self.isEconomic = None
        self.isComfort = None
        self._setpointNormal = None
        self._setpointEconomy = None
        self.modeList = SVT.modeDict.keys()
        self.modeIndex = None
        self._mode = None

        # Looking for all SVT devices
        devicesAPI = self.DomoticzAPI("type=command&param=getlightswitches")
        if devicesAPI:
            for device in devicesAPI["result"]:  # parse the switch device
                idx = int(device["idx"])
                #logger.debug("Processing device {} {}".format(device["Name"], idx))
                if "Name" in device:
                    if device["Name"] == "SVT - Thermostat Control":
                        self.controlId = idx
                        logger.debug(
                            "SVT - Thermostat Control idx: {}".format(idx))
                    elif device["Name"] == "SVT - Thermostat Pause":
                        self.pauseId = idx
                        logger.debug(
                            "SVT - Thermostat Pause idx: {}".format(idx))
                    elif device["Name"] == "SVT - Thermostat Mode":
                        self.modeId = idx
                        logger.debug(
                            "SVT - Thermostat Mode idx: {}".format(idx))

        # Looking for SVT Setpoints
        devicesAPI = self.DomoticzAPI(
            "type=devices&filter=utility&used=true&order=Name")
        if devicesAPI:
            for device in devicesAPI["result"]:  # parse the switch device
                idx = int(device["idx"])
                if "Name" in device:
                    if device["Name"] == "SVT - Setpoint Normal":
                        self.setpointNormalId = idx
                        logger.debug(
                            "SVT - Setpoint Normal idx: {}".format(idx))
                    elif device["Name"] == "SVT - Setpoint Economy":
                        self.setpointEconomyId = idx
                        logger.debug(
                            "SVT - Setpoint Economy idx: {}".format(idx))

        # Looking for SVT hardware
        devicesAPI = self.DomoticzAPI("type=hardware")
        if devicesAPI:
            for device in devicesAPI["result"]:  # parse the switch device
                if device["Name"] == "SVT":
                    self.indoorProbeId = device["Mode1"]
                    self.outdoorProbeId = device["Mode2"]
                    self.switchId = device["Mode3"]


    def rotate(self, l, y=1):
        if len(l) == 0:
            return l
        y = y % len(l)
        return l[y:] + l[:y]

    def nextMode(self):
        logger.debug(self.modeList)
        self.modeList = self.rotate(self.modeList)
        logger.debug(self.modeList)
        self.modeIndex = self.modeList[3]
        logger.debug(self.modeIndex)
        self._mode = SVT.modeDict[self.modeIndex]
        logger.debug(self._mode)
        return str(self._mode)

    def prevMode(self):
        self.modeList = self.rotate(self.modeList, -1)
        self.modeIndex = self.modeList[3]
        self._mode = SVT.modeDict[self.modeIndex]
        return str(self._mode)

    @property
    def mode(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.modeId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'Level' in res:
                level = res['Level']
                self._mode = level
                return Constants.mode[level]

    @mode.setter
    def mode(self, mode):
        inv_mode = {value: key for key, value in Constants.mode.items()}
        if type(mode) is str and mode in inv_mode:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd=Set Level&level={}"
                .format(self.modeId, inv_mode[mode]))
            if devicesAPI:
                self._mode = inv_mode[mode]
            else:
                logger.error("mode not in {}".format(inv_mode.keys()))
        elif type(mode) is int and mode in Constants.mode:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd=Set Level&level={}"
                .format(self.modeId, mode))
            if devicesAPI:
                self._mode = mode
            else:
                logger.error("mode not in {}".format(Constants.mode.keys()))

    @property
    def isNight(self):
        """ Whether the Mode is night mode

            :rtype: bool
        """
        return self.mode == 'nuit'

    @property
    def isDay(self):
        """ Whether the runningMode is Day mode

            :rtype: bool
        """
        return not self.isNight

    @property
    def state(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.controlId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'Level' in res:
                level = res['Level']
                self._mode = level
                return Constants.control[level]

    @state.setter
    def state(self, v):
        inv_control = {value: key for key, value in Constants.control.items()}
        if type(v) is str and v in inv_control:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd=Set Level&level={}"
                .format(self.controlId, inv_control[v]))
            if devicesAPI:
                self._state = inv_control[v]
            else:
                logger.error("state not in {}".format(inv_control.keys()))
        elif type(v) is int and v in Constants.control:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd=Set Level&level={}"
                .format(self.controlId, v))
            if devicesAPI:
                self._state = v
            else:
                logger.error("state not in {}".format(
                    Constants.control.keys()))

    @property
    def isOn(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.switchId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'Status' in res:
                level = res['Status']
                return level == 'On'

    @property
    def pause(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.pauseId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if "Status" in res:
                inv = {value: key for key,
                       value in Constants.switchState.items()}
                status = res['Status']
                self._pause = inv[status]
                return self._pause > 0

    @pause.setter
    def pause(self, v):
        inv = {value: key for key, value in Constants.switchState.items()}
        if type(v) is bool:
            if v is True:
                devicesAPI = self.DomoticzAPI(
                    "type=command&param=switchlight&idx={}&switchcmd={}"
                    .format(self.pauseId, 'On'))
            else:
                devicesAPI = self.DomoticzAPI(
                    "type=command&param=switchlight&idx={}&switchcmd={}"
                    .format(self.pauseId, 'Off'))
            if devicesAPI:
                self._pause = v
            else:
                logger.error("Pause value not in {}".format(inv.keys()))

        elif type(v) is int and v in Constants.switchState:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd={}"
                .format(self.pauseId, inv[v]))
            if devicesAPI:
                self._pause = v
            else:
                logger.error("Pause value not in {}".format(inv.keys()))
        elif type(v) is str and v in inv:
            devicesAPI = self.DomoticzAPI(
                "type=command&param=switchlight&idx={}&switchcmd={}"
                .format(self.pauseId, v))
            if devicesAPI:
                self._pause = inv[v]
            else:
                logger.error("Pause value not in {}".format(inv.keys()))

    @property
    def indoorTemp(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.indoorProbeId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'Temp' in res:
                self._indoorTemp = res['Temp']
                return res['Temp']

    @property
    def outdoorTemp(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.outdoorProbeId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'Temp' in res:
                return res['Temp']

    @property
    def setpointNormal(self):
        """ Read current setpointNormal

            :rtype: float
        """
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.setpointNormalId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'SetPoint' in res:
                setpoint = float(res['SetPoint'])
                self._setpointNormal = setpoint
                return setpoint

    @setpointNormal.setter
    def setpointNormal(self, v):
        """ Set current setpointNormal to v

            :rtype: float
        """
        logger.debug(v)
        if isinstance(v, int) or isinstance(v, float):
            self.DomoticzAPI(
                "type=command&param=setsetpoint&idx={}&setpoint={}".format(self.setpointNormalId, v))
            return v

    @property
    def setpointEconomy(self):
        devicesAPI = self.DomoticzAPI(
            "type=devices&rid={}".format(self.setpointEconomyId))
        if devicesAPI:
            res = devicesAPI["result"][0]
            if 'SetPoint' in res:
                setpoint = float(res['SetPoint'])
                self._setpointEconomy = setpoint
                return setpoint

    @setpointEconomy.setter
    def setpointEconomy(self, v):
        if isinstance(v, int) or isinstance(v, float):
            self.DomoticzAPI(
                "type=command&param=setsetpoint&idx={}&setpoint={}".format(self.setpointEconomyId, v))
            return v

    def getProbes(self):
        logger.debug("getProbes")
        devicesAPI = self.DomoticzAPI(
            "type=devices&filter=temp&used=true&order=ID")
        if devicesAPI:
            return devicesAPI["result"]

    def DomoticzAPI(self, APICall):
        start = time.time()
        resultJson = None
        url = "https://{}/json.htm?{}".format(
            self.ip, urllib.quote(APICall, '&='))

        req = request.Request(url)

        if self.username != "":
            # logger.debug(
            #     "Add authentification for user {}".format(self.username))
            credentials = ('%s:%s' % (self.username, self.password))
            encoded_credentials = base64.b64encode(
                credentials.encode('ascii'))
            req.add_header('Authorization', 'Basic %s' %
                           encoded_credentials.decode("ascii"))
        try:
            response = request.urlopen(req)
        except request.URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            logger.error(
                "Domoticz API: http error = {}".format(response.status))
        else:
            resultJson = json.loads(response.read().decode('utf-8'))
            # logger.debug(resultJson["status"])
            if resultJson["status"] != "OK":
                logger.error("Domoticz API returned an error: status = {}".format(
                    resultJson["status"]))
                resultJson = None
                return resultJson
            else:
                elapsed = (time.time() - start) * 1000
                logger.debug(
                    "Calling domoticz API: {}  [{:.0f} ms]".format(url, elapsed))
                return resultJson
