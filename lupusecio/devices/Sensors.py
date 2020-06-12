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

from lupusecio.devices.Generic import GenericZoneDevice
import lupusecio.constants as GENERAL

class BinarySensor(GenericZoneDevice):

    def __init__(self, name, device_type, zone_id, status):
        super().__init__(name, device_type, zone_id)
        self._status = status

    def set_status(self, status):
        self._status = status

    def get_status(self):
        return self._status

    def __str__(self):
        return "%s, Status: %s" % (super().__str__(), self._status)

    def is_on_open(self):
        return self._status == GENERAL.SensorStatus.OPEN | self._status == GENERAL.SensorStatus.ON

    def is_off_closed(self):
        return self._status == GENERAL.SensorStatus.CLOSED | self._status == GENERAL.SensorStatus.OFF

