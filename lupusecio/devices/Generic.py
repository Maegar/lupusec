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

class GenericDevice(object):

    def __init__(self, name, device_type, battery = None, tamper = False):
        self._name = name
        self._tamper = tamper
        self._battery = battery
        self._device_type = device_type

    def get_battery(self):
        return self._battery
    
    def set_battery(self, status):
        self._battery = status


    def is_tamper(self):
        return self._tamper

    def set_tamper(self, tamper):
        self._tamper = tamper

    def __str__(self):
        return "Type: %s, Name: %s, Battery: %s, Tamper: %d" % (self._device_type, self._name, self._battery, self._tamper)


class GenericZoneDevice(GenericDevice):
    
    def __init__(self, name, device_type, zone_id):
        super().__init__(name, device_type)
        self.zone_id = zone_id
    
    def __str__(self):
        return "Zone: %s, %s" % (self.zone_id, super().__str__())