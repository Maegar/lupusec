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

from lupusecio.devices.Generic import GenericDevice, GenericZoneDevice
from lupusecio.devices.Sensors import BinarySensor
import lupusecio.constants as GENERAL

class AlarmPanel(GenericDevice):

    def __init__(self, name, lupusec_system):
        super().__init__(name, GENERAL.DeviceType.TYPE_ALARM_PANEL)
        self._lupusec_system = lupusec_system
        self._sensors = {}
        self._history = None
        self.do_update()

    def get_history(self):
        return self._history

    def get_sensors(self):
        return self._sensors

    def do_update_history(self):
        pass

    def do_update_sensors(self):
        pass

    def do_update_cameras(self):
        pass

    def do_update(self):
        self.do_update_history()
        self.do_update_sensors()
        #doUpdateCameras()

class XT1AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'historyGet'
    ACTION_SENSOR_LIST_GET = 'sensorListGet'
    ACTION_PANEL_CONDITION_ENDPOINT = 'panelCondGet'

    MODES = {'Arm': GENERAL.Mode.ARM, 
             'Home': GENERAL.Mode.HOME, 
             'Disarm': GENERAL.Mode.DISARM}

    STATUS = {'': GENERAL.SensorStatus.CLOSED, 
              'Geschlossen': GENERAL.SensorStatus.CLOSED, 
              'Offen': GENERAL.SensorStatus.OPEN}
    
    BATTERY_STATUS = {'': GENERAL.BatteryStatus.NORMAL,
                      'Normal': GENERAL.BatteryStatus.NORMAL,
                      'Fehler': GENERAL.BatteryStatus.TROUBLE}

    TAMPER_STATUS = {'Geschlossen': False,
                     'Offen': True,
                     '': True}

    TYPES = {'Fensterkontakt': GENERAL.DeviceType.TYPE_WINDOW_SENSOR,
             'Türkontakt': GENERAL.DeviceType.TYPE_DOOR_SENSOR,
             'Keypad': GENERAL.DeviceType.TYPE_KEY_PAD, 
             'Steckdose': GENERAL.DeviceType.TYPE_POWER_SWITCH,
             'Bewegungsmelder': GENERAL.DeviceType.TYPE_MOTION_DETECTOR, 
             'Rauchmelder': GENERAL.DeviceType.TYPE_SMOKE_DETECOR, 
             'Wassermelder': GENERAL.DeviceType.TYPE_WATER_DETECTOR}

    def __init__(self, lupusecSystem):
        super().__init__("XT 1 Zentrale", lupusecSystem)
        self.do_update_panel_cond()

    def do_update_panel_cond(self):
        panel_conditions = self._lupusec_system.do_get_js(self.ACTION_PANEL_CONDITION_ENDPOINT)
        self._mode = self._evaluate_panel_condition(panel_conditions, 'mode_st', self.MODES)
        self._battery = self._evaluate_panel_condition(panel_conditions, 'battery', self.BATTERY_STATUS)
        self._tamper = self._evaluate_panel_condition(panel_conditions, 'tamper', self.TAMPER_STATUS)

    def _evaluate_panel_condition(self, panel_conditions, field, enum):
        if panel_conditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panel_conditions['updates'][field]] 

    def do_update(self):
        super().do_update()
        self.do_update_panel_cond

    def do_update_sensors(self):
        sensor_list = self._lupusec_system.do_get_js(self.ACTION_SENSOR_LIST_GET)['senrows']
        for device in sensor_list:
            
            device_name = device['name']
            device_id = device['no']
            device_zone_id = device ['zone']

            def _evaluate_in_type(field_name, enum):
                if device[field_name] not in enum:
                    return 'UNKNOWN'
                else:
                    return enum[device[field_name]]

            device_type = _evaluate_in_type('type', self.TYPES)
            device_battery = _evaluate_in_type('battery', self.BATTERY_STATUS)
            device_tamper = _evaluate_in_type('tamp', self.TAMPER_STATUS)

            _device = self._sensors.get(device_id)
            _is_update = True if _device else False
            if device_type in GENERAL.BINARY_SENSOR_TYPES:
                status = self.STATUS[device['cond']]
                if not _is_update:
                    _device = BinarySensor(device_name, device_type, device_zone_id, status)
                else:
                    _device.set_status(status)

            else:
                _device = GenericZoneDevice(device_name, device_type, device_zone_id)

            _device.set_battery(device_battery)
            _device.set_tamper(device_tamper)
            if not _is_update:
                self._sensors[device_id] = _device
 
    def do_update_history(self):
        self._history = []
        for entry in self._lupusec_system.do_get_js(self.ACTION_HISTORY_GET)['hisrows']:
            self._history.append({'date': entry['d'], 'time': entry['t'], 'Sensor': entry['s'], 'Event': entry['a']})

    def __str__(self):
        return "%s, Mode: %s" % (super().__str__(), self._mode)
    
    

class XT2AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'historyGet'
    ACTION_SENSOR_LIST_GET = 'deviceListGet'
    ACTION_PANEL_CONDITION_GET = 'panelCondGet'

    MODES = {r'{AREA_MODE_0}': GENERAL.Mode.ARM, 
             r'{AREA_MODE_1}': GENERAL.Mode.HOME, 
             r'{AREA_MODE_2}': GENERAL.Mode.DISARM}

    STATUS = {r'{WEB_MSG_DC_CLOSE}': GENERAL.SensorStatus.CLOSED, 
              r'{WEB_MSG_DC_OPEN}': GENERAL.SensorStatus.OPEN}
    
    BATTERY_STATUS = {True: GENERAL.BatteryStatus.NORMAL,
                      False: GENERAL.BatteryStatus.TROUBLE}

    TYPES = {4: GENERAL.DeviceType.TYPE_WINDOW_SENSOR,
             37: GENERAL.DeviceType.TYPE_KEY_PAD,
             23: GENERAL.DeviceType.TYPE_SIRENE,
             46: GENERAL.DeviceType.TYPE_SIRENE,}

    def __init__(self, lupusec_system):
        super().__init__("XT2 Zentrale", lupusec_system)
        self.do_update_panel_cond()
    
    def do_update_sensors(self):
        sensor_list = self._lupusec_system.do_get_json(self.ACTION_SENSOR_LIST_GET)['senrows']
        for device in sensor_list:    
            device_name = device['name']
            device_zone_id = device['zone']
            device_tamper = False if int(device['tamper_ok']) else True
            device_battery = False if int(device['battery_ok']) else True

            if device['type'] not in self.TYPES:
                device_type = 'UNKNOWN'
            else:
                device_type = self.TYPES[device['type']]

            _device = self._sensors.get(device_zone_id)
            _is_update = True if _device else False
            if device_type in GENERAL.BINARY_SENSOR_TYPES:
                status = self.STATUS[device['status']]
                if not _is_update:
                    _device = BinarySensor(device_name, device_type, device_zone_id, status)
                else:
                    _device.set_status(status)

            else:
                _device = GenericZoneDevice(device_name, device_type, device_zone_id)

            _device.set_battery(device_battery)
            _device.set_tamper(device_tamper)
            if not _is_update:
                self._sensors[device_zone_id] = _device

    def do_update_panel_cond(self):
        panel_conditions = self._lupusec_system.do_get_json(self.ACTION_PANEL_CONDITION_GET)
        self._mode_area1 = self._evaluate_panel_condition(panel_conditions, 'mode_a1', self.MODES)
        self._mode_area2 = self._evaluate_panel_condition(panel_conditions, 'mode_a2', self.MODES)
        self._battery = self._evaluate_panel_condition(panel_conditions, 'battery_ok', {'1': True, '0': False})
        self._tamper = self._evaluate_panel_condition(panel_conditions, 'tamper_ok', {'1': True, '0': False})

    def _evaluate_panel_condition(self, panel_conditions, field, enum):
        if panel_conditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panel_conditions['updates'][field]]
    
    def do_update_history(self):
        self._history = []
        for entry in self._lupusec_system.do_get_json(self.ACTION_HISTORY_GET)['hisrows']:
            self._history.append({'date': entry['d'], 'time': entry['t'], 'Sensor': entry['s'], 'Event': entry['a']})
    
    def __str__(self):
        return "%s, mode_area1: %s, mode_area2: %s" % (super().__str__(), self._mode_area1, self._mode_area2)

   