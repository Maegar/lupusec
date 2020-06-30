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

class XT1AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'historyGet'
    ACTION_SENSOR_LIST_GET = 'sensorListGet'
    ACTION_PANEL_CONDITION_ENDPOINT = 'panelCondGet'

    def __init__(self, lupusecSystem):
        super().__init__("XT 1 Zentrale", lupusecSystem)
        self.do_update_panel_cond()

    def do_update_panel_cond(self):
        """ Update pandel conditions """
        panel_conditions = self._lupusec_system.do_get_js(self.ACTION_PANEL_CONDITION_ENDPOINT)
        self._mode = panel_conditions['updates']['mode_st']
        self._battery = True if panel_conditions['updates']['battery'] == '' else panel_conditions['updates']['battery']
        self._tamper = True if panel_conditions['updates']['tamper'] == '' else panel_conditions['updates']['tamper']

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
        return "%s, Mode: %s" % (super().__str__(), self._mode)
    
    

class XT2AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'recordListGet'
    ACTION_SENSOR_LIST_GET = 'deviceListGet'
    ACTION_PANEL_CONDITION_GET = 'panelCondGet'

    def __init__(self, lupusec_system):
        super().__init__("XT2 Zentrale", lupusec_system)
        self.do_update_panel_cond()
    
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
        panel_conditions = self._lupusec_system.do_get_json(self.ACTION_PANEL_CONDITION_GET)
        self._mode_area1 = self._evaluate_panel_condition(panel_conditions, 'mode_a1', TRANS.XT2_TRANSLATIONS)
        self._mode_area2 = self._evaluate_panel_condition(panel_conditions, 'mode_a2', TRANS.XT2_TRANSLATIONS)
        self._battery = self._evaluate_panel_condition(panel_conditions, 'battery_ok', {'1': True, '0': False})
        self._tamper = self._evaluate_panel_condition(panel_conditions, 'tamper_ok', {'1': True, '0': False})

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
        return "%s, mode_area1: %s, mode_area2: %s" % (super().__str__(), self._mode_area1, self._mode_area2)

   