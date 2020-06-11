class GenericDevice(object):

    def __init__(self, name, deviceType, battery = None, tamper = False):
        self._name = name
        self._tamper = tamper
        self._battery = battery
        self._deviceType = deviceType

    def getBattery(self):
        return self._battery
    
    def setBattery(self, status):
        self._battery = status


    def isTamper(self):
        return self._tamper

    def setTamper(self, tamper):
        self._tamper = tamper

    def __str__(self):
        return "Type: %s, Name: %s, Battery: %s, Tamper: %d" % (self._deviceType, self._name, self._battery, self._tamper)


class GenericZoneDevice(GenericDevice):
    
    def __init__(self, name, deviceType, zoneId):
        super().__init__(name, deviceType)
        self._zoneId = zoneId
    
    def __str__(self):
        return "Zone: %s, %s" % (self._zoneId, super().__str__())