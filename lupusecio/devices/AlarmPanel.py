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

""" Alarm panel module

Can be used to retrieve information and trigger actions from alarm panel.
"""

import requests
import json

from lupusecio.devices.Generic import GenericDevice
import lupusecio.devices.Translation as TRANS

class AlarmPanel(object):
    """ Generic alarm panel """

    def __init__(self, name, lupusec_system):
        self._name = name
        self._lupusec_system = lupusec_system
        self._sensors = {}
        self._history = None
        self.do_update()

    def get_history(self):
        """ Retrieves history logs """
        return self._history

    def get_sensors(self):
        """ Retrieves all sensors """
        return self._sensors

    def do_update_history(self):
        """ Update the history """
        pass

    def do_update_sensors(self):
        """ Update the sensors """
        pass

    def do_update_cameras(self):
        """ Update the camera settings """
        pass

    def do_update(self):
        """ do update for all """
        self.do_update_history()
        self.do_update_sensors()
        #doUpdateCameras()

    def __str__(self):
        return "Lupusec: %s" % (self._name)

class Area(object):

    ACTION_PANEL_CONDITION_ENDPOINT_POST = 'panelCondPost'

    def __init__(self, alarmPanel, panelConditions, areaNo = None):
        self.alarmPanel = alarmPanel
        self.areaNo = areaNo
        if panelConditions['updates']['alarm_ex'] == 1 or not 'Normal':
            self._mode = 'TRIGGERED'
        else:
            fieldValue = 'pcondform' + (str(self.areaNo) if self.areaNo is not None else "")
            self._mode = self.alarmPanel.MODE_TRANSLATION[panelConditions['forms'][fieldValue]['mode']]
    
    def set_mode(self, modeToSwitch):
        """ Set the new mode corresponding to the given value
        If requests fails false will be returned otherwise true
        """
        flippedValues = dict([(value, key) for key, value in self.alarmPanel.MODE_TRANSLATION.items()])
        dataToSend = {'mode':flippedValues[modeToSwitch]}
        if self.areaNo is not None:
            dataToSend.update("area", self.areaNo)
        request = self.alarmPanel._lupusec_system.do_post_js(self.ACTION_PANEL_CONDITION_ENDPOINT_POST, )

        return request['result'] == 1

    def get_mode(self):
        return self._mode

    def is_arm(self):
        return self._mode == 'ARM'

    def is_home(self):
        return self._mode == 'HOME'

    def is_night(self):
        return self._mode == 'HOME2'

    def is_custom_bypass(self):
        return self._mode == 'HOME3'
    
    def is_disarm(self):
        return self._mode == 'DISARM'

    def is_triggered(self):
        return self._mode == 'TRIGGERED'

    def __str__(self):
        return json.dumps(self.set_mode(self._mode))  
    

class XT1AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'historyGet'
    ACTION_SENSOR_LIST_GET = 'sensorListGet'
    ACTION_PANEL_CONDITION_ENDPOINT = 'panelCondGet'

    MODE_ALARM_TRIGGERED = 'Einbruch'
    MODE_TRANSLATION = {'2' : 'DISARM', '1' : 'HOME', '0' : 'ARM'}

    def __init__(self, lupusecSystem):
        super().__init__("XT 1 Zentrale", lupusecSystem)
        self.do_update_panel_cond()

    def do_update_panel_cond(self):
        """ Update pandel conditions """
        self._panel_conditions = self._lupusec_system.do_get_js(self.ACTION_PANEL_CONDITION_ENDPOINT)
        self.area = Area(self, self._panel_conditions)
        self._battery = True if self._panel_conditions['updates']['battery'] == '' else self._panel_conditions['updates']['battery']
        self._tamper = True if self._panel_conditions['updates']['tamper'] == '' else self._panel_conditions['updates']['tamper']

    def do_update(self):
        """ Update all information """
        super().do_update()
        self.do_update_panel_cond

    def do_update_sensors(self):
        sensor_list = self._lupusec_system.do_get_js(self.ACTION_SENSOR_LIST_GET)['senrows']
        for device in sensor_list:
            device_type = device['type']
            device_name = device['name']
            device_area_id = '0'
            device_zone_id = device['zone']
            device_status = ''

            device_tamper_ok = device['tamp'] == ''
            device_tamper_status = '' if device_tamper_ok else device['tamp']

            device_battery_ok = device['battery'] == ''
            device_battery_status = '' if device_battery_ok else device['battery']

            device_cond_ok = device['cond']
            device_cond_status = '' if device_cond_ok else device['cond']

            _id = '%s-%s' % (device_area_id, device_zone_id)
            _device = self._sensors.get(_id)
            if not _device:
                _device = GenericDevice(device_area_id, device_zone_id, device_name, device_type)
                self._sensors[_id] = _device
            
            _device.set_battery(device_battery_ok, device_battery_status)
            _device.set_tamper(device_tamper_ok, device_tamper_status)
            _device.set_cond(device_cond_ok, device_cond_status)
            _device.set_status(device_status)
 
    def do_update_history(self):
        self._history = []
        for entry in self._lupusec_system.do_get_js(self.ACTION_HISTORY_GET)['hisrows']:
            self._history.append({'date': entry['d'], 'time': entry['t'], 'Sensor': entry['s'], 'Event': entry['a']})

    def __str__(self):
        return "%s, Mode: %s" % (super().__str__(), self.area.get_mode())
    

class XT2AlarmPanel(AlarmPanel):
    ACTION_HISTORY_GET = 'recordListGet'
    ACTION_SENSOR_LIST_GET = 'deviceListGet'
    ACTION_PANEL_CONDITION_GET = 'panelCondGet'
    MODE_TRANSLATION = {'4' : 'HOME3', '3' : 'HOME2', '2' : 'HOME', '0' : 'DISARM', '1' : 'ARM'}

    def __init__(self, lupusec_system):
        super().__init__("XT2 Zentrale", lupusec_system)
        self.do_update_panel_cond()
    
    def do_update_mode(self, area):
        self._lupusec_system.do_post_json()

    def do_update_sensors(self):
        sensor_list = self._lupusec_system.do_get_json(self.ACTION_SENSOR_LIST_GET)['senrows']
        for device in sensor_list:

            device_type = TRANS.XT2_TRANSLATIONS[device['type_f']]
            device_name = device['name']
            device_area_id = device['area']
            device_zone_id = device['zone']
            device_status = '' if device['status'] == '' else TRANS.XT2_TRANSLATIONS[device['status']]

            device_tamper_ok = int(device['tamper_ok'])
            device_tamper_status = '' if device_tamper_ok else TRANS.XT2_TRANSLATIONS[device['tamper']]

            device_battery_ok = int(device['battery_ok'])
            device_battery_status = '' if device_battery_ok else TRANS.XT2_TRANSLATIONS[device['battery']]

            device_cond_ok = int(device['cond_ok'])
            device_cond_status = '' if device_cond_ok else TRANS.XT2_TRANSLATIONS[device['cond']]

            _id = '%s-%s' % (device_area_id, device_zone_id)
            _device = self._sensors.get(_id)
            if not _device:
                _device = GenericDevice(device_area_id, device_zone_id, device_name, device_type)
                self._sensors[_id] = _device
            
            _device.set_battery(device_battery_ok, device_battery_status)
            _device.set_tamper(device_tamper_ok, device_tamper_status)
            _device.set_cond(device_cond_ok, device_cond_status)
            _device.set_status(device_status)

    def do_update_panel_cond(self):
        self._panel_conditions = self._lupusec_system.do_get_json(self.ACTION_PANEL_CONDITION_GET)
        self.area1 = Area(self, self._panel_conditions, 1)
        self.area2 = Area(self, self._panel_conditions, 2)
        self._battery = self._evaluate_panel_condition(self._panel_conditions, 'battery_ok', {'1': True, '0': False})
        self._tamper = self._evaluate_panel_condition(self._panel_conditions, 'tamper_ok', {'1': True, '0': False})

    def _evaluate_panel_condition(self, panel_conditions, field, enum):
        if panel_conditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panel_conditions['updates'][field]]
    
    def do_update_history(self):
        self._history = []
        for entry in self._lupusec_system.do_get_json(self.ACTION_HISTORY_GET)['logrows']:
            indexEventEnd = entry['event'].index('}')
            eventName = entry['event'][0:indexEventEnd+1]
            event = TRANS.XT2_TRANSLATIONS[eventName]
            if '%s' in event:
                event = event % (entry['area'])
            self._history.append({'date': entry['time'], 'time': entry['time'], 'Sensor': entry['name'], 'Type': TRANS.XT2_TRANSLATIONS[entry['type_f']], 'Event': event})
    
    def __str__(self):
        return "%s, mode_area1: %s, mode_area2: %s" % (super().__str__(), self.area1.get_mode(), self.area2.get_mode())
