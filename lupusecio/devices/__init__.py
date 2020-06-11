import requests
import demjson

from lupusecio.devices.AlarmPanel import *
from lupusecio.devices.Sensors import *

class LupusecSystem(object):

    def __init__(self, username, password, url, unverified_ssl=False):
        self._session = requests.Session()
        self._alarm_panel_url = url
        self._session.auth = (username, password)
        self.sensors = []

    def doGet(self, endpoint):
        response = self._session.get(self._alarm_panel_url + '/action/' + endpoint, timeout=15)
        jsData = self.__clean_json(response.text)
        return demjson.decode(jsData)

    def __clean_json(self, textdata):
            textdata = textdata.replace("\t", "")
            if textdata.startswith("/*-secure-"):
                textdata = textdata[10:-2]
            
            return textdata
