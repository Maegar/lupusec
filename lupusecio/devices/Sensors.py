from lupusecio.devices.Generic import GenericZoneDevice
import lupusecio.constants as GENERAL

class BinarySensor(GenericZoneDevice):

    def __init__(self, name, deviceType, zoneId, status):
        super().__init__(name, deviceType, zoneId)
        self._status = status

    def setStatus(self, status):
        self._status = status

    def getStatus(self):
        return self._status

    def __str__(self):
        return "%s, Status: %s" % (super().__str__(), self._status)

    def is_on_open(self):
        return self._status == GENERAL.SensorStatus.OPEN | self._status == GENERAL.SensorStatus.ON

    def is_off_closed(self):
        return self._status == GENERAL.SensorStatus.CLOSED | self._status == GENERAL.SensorStatus.OFF

