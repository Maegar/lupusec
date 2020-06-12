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

from enum import Enum

class SensorStatus(Enum):
    OPEN = 1
    CLOSED = 0
    ON = 1
    OFF = 0 

class BatteryStatus(Enum):
    NONE = 0
    NORMAL = 1
    TROUBLE = 2

class Mode(Enum):
    ARM = 0
    HOME = 1
    DISARM = 2

class DeviceType(Enum):
    TYPE_ALARM_PANEL = 0
    TYPE_WINDOW_SENSOR = 1
    TYPE_DOOR_SENSOR = 2
    TYPE_KEY_PAD = 3
    TYPE_MOTION_DETECTOR = 4
    TYPE_SMOKE_DETECOR = 5
    TYPE_WATER_DETECTOR = 6
    TYPE_POWER_SWITCH = 7
    TYPE_SIRENE = 8

SWITCH_TYPES = [DeviceType.TYPE_POWER_SWITCH]
BINARY_SENSOR_TYPES = [DeviceType.TYPE_DOOR_SENSOR, DeviceType.TYPE_WINDOW_SENSOR]
TYPE_SENSOR = [DeviceType.TYPE_SMOKE_DETECOR, DeviceType.TYPE_WATER_DETECTOR, DeviceType.TYPE_MOTION_DETECTOR]
