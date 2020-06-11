import requests

from lupusecio.devices.Generic import GenericDevice, GenericZoneDevice
from lupusecio.devices.Sensors import BinarySensor
import lupusecio.constants as GENERAL

class AlarmPanel(GenericDevice):

    def __init__(self, name, lupusecSystem):
        super().__init__(name, GENERAL.DeviceType.TYPE_ALARM_PANEL)
        self._lupusecSystem = lupusecSystem
        self._sensors = {}
        self._history = None
        self.doUpdate()

    def getHistory(self):
        return self._history

    def getSensors(self):
        return self._sensors

    def doUpdateHistory(self):
        pass

    def doUpdateSensors(self):
        pass

    def doUpdateCameras(self):
        pass

    def doUpdate(self):
        self.doUpdateHistory()
        self.doUpdateSensors()
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
        self.doUpdatePanelCond()

    def doUpdatePanelCond(self):
        panelConditions = self._lupusecSystem.doGet(self.ACTION_PANEL_CONDITION_ENDPOINT)
        self._mode = self._evaluatePanelCondition(panelConditions, 'mode_st', self.MODES)
        self._battery = self._evaluatePanelCondition(panelConditions, 'battery', self.BATTERY_STATUS)
        self._tamper = self._evaluatePanelCondition(panelConditions, 'tamper', self.TAMPER_STATUS)

    def _evaluatePanelCondition(self, panelConditions, field, enum):
        if panelConditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panelConditions['updates'][field]] 

    def doUpgrade(self):
        super().doUpdate()
        self.doUpdatePanelCond

    def doUpdateSensors(self):
        sensorList = self._lupusecSystem.doGet('sensorListGet')['senrows']
        for device in sensorList:
            
            deviceName = device['name']
            deviceId = device['no']
            deviceZoneId = device ['zone']

            def _evaluateInType(fieldName, enum):
                if device[fieldName] not in enum:
                    return 'UNKNOWN'
                else:
                    return enum[device[fieldName]]

            deviceType = _evaluateInType('type', self.TYPES)
            deviceBattery = _evaluateInType('battery', self.BATTERY_STATUS)
            deviceTamper = _evaluateInType('tamp', self.TAMPER_STATUS)

            _device = self._sensors.get(deviceId)
            _isUpdate = True if _device else False
            if deviceType in GENERAL.BINARY_SENSOR_TYPES:
                status = self.STATUS[device['cond']]
                if not _isUpdate:
                    _device = BinarySensor(deviceName, deviceType, deviceZoneId, status)

                _device.setStatus(status)

            else:
                _device = GenericZoneDevice(deviceName, deviceType, deviceZoneId)

            _device.setBattery(deviceBattery)
            _device.setTamper(deviceTamper)
            if not _isUpdate:
                self._sensors[deviceId] = _device
 
    def doUpdateHistory(self):
        self._history = []
        for entry in self._lupusecSystem.doGet(self.ACTION_HISTORY_GET)['hisrows']:
            self._history.append({'date': entry['d'], 'time': entry['t'], 'Sensor': entry['s'], 'Event': entry['a']})

    def __str__(self):
        return "%s, Mode: %s" % (super().__str__(), self._mode)
    
    

class XT2AlarmPanel(AlarmPanel):

    ACTION_HISTORY_GET = 'historyGet'
    ACTION_SENSOR_LIST_GET = 'sensorListGet'
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

    def __init__(self, lupusecSystem):
        super().__init__("XT2 Zentrale", lupusecSystem)
        self.doUpdatePanelCond()
    
    def doUpdateSensors(self):
        sensorList = self._lupusecSystem.doGet(self.ACTION_SENSOR_LIST_GET)['senrows']
        for device in sensorList:    
            deviceName = device['name']
            deviceZoneId = device['zone']
            deviceTamper = False if int(device['tamper_ok']) else True
            deviceBattery = False if int(device['battery_ok']) else True

            if device['type'] not in self.TYPES:
                deviceType = 'UNKNOWN'
            else:
                deviceType = self.TYPES[device['type']]

            _device = self._sensors.get(deviceZoneId)
            _isUpdate = True if _device else False
            if deviceType in GENERAL.BINARY_SENSOR_TYPES:
                status = self.STATUS[device['status']]
                if not _isUpdate:
                    _device = BinarySensor(deviceName, deviceType, deviceZoneId, status)

                _device.setStatus(status)

            else:
                _device = GenericZoneDevice(deviceName, deviceType, deviceZoneId)

            _device.setBattery(deviceBattery)
            _device.setTamper(deviceTamper)
            if not _isUpdate:
                self._sensors[deviceZoneId] = _device

    def doUpdatePanelCond(self):
        panelConditions = self._lupusecSystem.doGet(self.ACTION_PANEL_CONDITION_GET)
        self._mode_area1 = self._evaluatePanelCondition(panelConditions, 'mode_a1', self.MODES)
        self._mode_area2 = self._evaluatePanelCondition(panelConditions, 'mode_a2', self.MODES)
        self._battery = self._evaluatePanelCondition(panelConditions, 'battery_ok', {'1': True, '0': False})
        self._tamper = self._evaluatePanelCondition(panelConditions, 'tamper_ok', {'1': True, '0': False})

    def _evaluatePanelCondition(self, panelConditions, field, enum):
        if panelConditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panelConditions['updates'][field]]
    
    def doUpdateHistory(self):
        self._history = []
        for entry in self._lupusecSystem.doGet(self.ACTION_HISTORY_GET)['hisrows']:
            self._history.append({'date': entry['d'], 'time': entry['t'], 'Sensor': entry['s'], 'Event': entry['a']})
    
    def __str__(self):
        return "%s, mode_area1: %s, mode_area2: %s" % (super().__str__(), self._mode_area1, self._mode_area2)

   