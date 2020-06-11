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

    ACTION_SENSOR_LIST_GET = 'sensorListGet'
    ACTION_PANEL_CONDITION_ENDPOINT = 'panelCondGet'

    MODES = {'Arm': GENERAL.Mode.ARM, 
             'Home': GENERAL.Mode.HOME, 
             'Disarm': GENERAL.Mode.DISARM}

    STATUS = {'': GENERAL.SensorStatus.CLOSED, 
              'Geschlossen': GENERAL.SensorStatus.CLOSED, 
              'Offen': GENERAL.SensorStatus.OPEN}
    
    BATTERY_STATUS = {'': GENERAL.BatteryStatus.NONE,
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
        self._mode = self._evaluateMode(panelConditions)
        self._battery = self._evaluateBattery(panelConditions)
        self._tamper = self._evaluateTamper(panelConditions)

    def _evaluateMode(self, panelConditions):
        return self._evaluatePanelCondition(panelConditions, 'mode_st', self.MODES)

    def _evaluateBattery(self, panelConditions):
        return self._evaluatePanelCondition(panelConditions, 'battery', self.BATTERY_STATUS)
    
    def _evaluateTamper(self, panelConditions):
        return self._evaluatePanelCondition(panelConditions, 'tamper', self.TAMPER_STATUS)

    def _evaluatePanelCondition(self, panelConditions, field, enum):
        if panelConditions['updates'][field] not in enum:
            return 'UNKNOWN'
        else:
            return enum[panelConditions['updates'][field]] 

    def doUpdateSensors(self):
        sensorList = self._lupusecSystem.doGet('sensorListGet')['senrows']
        for device in sensorList:
            
            deviceName = device['name']
            deviceId = device['no']
            deviceZoneId = device ['zone']

            if device['type'] not in self.TYPES:
                deviceType = 'UNKNOWN'
            else:
                deviceType = self.TYPES[device['type']]

            _device = self._sensors.get(deviceId)
            if deviceType in GENERAL.BINARY_SENSOR_TYPES:
                status = self.STATUS[device['cond']]
                if _device:
                    _device.setStatus(status)
                else:
                    lupuDev = BinarySensor(deviceName, deviceType, deviceZoneId, status)
            else:
                lupuDev = GenericZoneDevice(deviceName, deviceType, deviceZoneId)

            if not _device:
                self._sensors[deviceId] = lupuDev
        

    def isArm(self):
        return self._mode == GENERAL.Mode.ARM

    def isDisarm(self):
        return self._mode == GENERAL.Mode.DISARM

    def isHome(self):
        return self._mode == GENERAL.Mode.HOME

    def getMode(self):
        return self._mode

    def __str__(self):
        return "%s, Mode: %s" % (super().__str__(), self._mode)
    
    

class XT2AlarmPanel(AlarmPanel):

    ACTION_SENSOR_LIST_GET = 'sensorListGet'
    ACTION_PANEL_CONDITION_GET = 'panelCondGet'

    MODES = {'Arm': GENERAL.Mode.ARM, 
             'Home': GENERAL.Mode.HOME, 
             'Disarm': GENERAL.Mode.DISARM}

    STATUS = {r'{WEB_MSG_DC_CLOSE}': GENERAL.SensorStatus.CLOSED, 
              r'{WEB_MSG_DC_OPEN}': GENERAL.SensorStatus.OPEN}

    TYPES = {4: GENERAL.DeviceType.TYPE_WINDOW_SENSOR,
             37: GENERAL.DeviceType.TYPE_KEY_PAD,
             23: GENERAL.DeviceType.TYPE_SIRENE,
             46: GENERAL.DeviceType.TYPE_SIRENE,}

    def __init__(self, name, lupusecSystem):
        super().__init__("XT2 Zentrale", lupusecSystem)
        #self._mode_area1 = resp
        #self._mode_area2 = resp

   