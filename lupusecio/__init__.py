"""
class XT2(LupusecSystem):
    def __init__(self, username, password, url):
        super().__init__(username, password, url)

    def getDeviceList(self):w
        sensorList = self.doGet('/deviceListGet')['senrows']
        for device in sensorList:    
            deviceName = device['name']
            deviceId = device['zone']
            deviceTamper = False if int(device['tamper_ok']) else True

            if device['type'] not in XT2_CONST.TYPES:
                deviceType = 'UNKNOWN'
            else:
                deviceType = XT2_CONST.TYPES[device['type']]

            if deviceType in GENERAL.BINARY_SENSOR_TYPES:
                status = XT2_CONST.STATUS[device['status']]
                lupuDev = BinaryDevice(status, deviceId, deviceName, deviceType, deviceTamper)
            else:
                lupuDev = Device(deviceId, deviceName, deviceType, deviceTamper)

            self.sensors.append(lupuDev)  
        return self.sensors

    def getAlarmPanelStatus(self):
        return self.doGet('/panelCondGet')
    
    def doGet(self, url):
        jsData = super().doGet(url)
        return json.loads(self.__clean_json(jsData))

    def __clean_json(self, textdata):
        return textdata.replace('\t', '')
"""