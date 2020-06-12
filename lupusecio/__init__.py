#!/usr/bin/env python3
# Copyright 2020 Paul Proske
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import demjson

class LupusecSystem(object):

    def __init__(self, username, password, url, verify_ssl=True):
        self._session = requests.Session()
        self._session.verify=verify_ssl
        self._alarm_panel_url = url
        self._session.auth = (username, password)
        self.sensors = []

    def do_get(self, endpoint):
        response = self._session.get(self._alarm_panel_url + '/action/' + endpoint, timeout=15)
        jsData = self.__clean_json(response.text)
        return demjson.decode(jsData)

    def __clean_json(self, textdata):
            textdata = textdata.replace("\t", "")
            if textdata.startswith("/*-secure-"):
                textdata = textdata[10:-2]
            
            return textdata
