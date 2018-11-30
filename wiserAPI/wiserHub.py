"""
Wiser API Facade

Currently embedded in the Home Assistant API but will be split into PyPi

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com

"""

import logging
import requests

_LOGGER = logging.getLogger(__name__)
WISERHUBURL = "http://{}/data/domain/"



class wiserHub():
   

    def __init__(self,hubIP,secret):
        _LOGGER.info("WiserHub API Init")
        self.wiserHubData=None
        self.hubIP=hubIP
        self.hubSecret=secret
        self.headers = {'SECRET': self.hubSecret}
        self.device2roomMap={}      # Dict holding Valve2Room mapping convinience variable
        self.refreshData()          # Issue first refresh in init
        
    def refreshData(self):
        smartValves=[]
        _LOGGER.info("Updating Wiser Hub Data")
        self.wiserHubData = requests.get(WISERHUBURL.format(
            self.hubIP), headers=self.headers).json()
        _LOGGER.debug("Wiser Hub Data received {} ".format(self.wiserHubData))
        for room in self.getRooms():
            roomStatId=room.get("RoomStatId")
            if roomStatId!=None:
                #RoomStat found add it to the list
                self.device2roomMap[roomStatId]={"roomId":room.get("id"), "roomName":room.get("Name")}
            smartValves=room.get("SmartValveIds")
            if smartValves!=None:
                for valveId in smartValves:
                        self.device2roomMap[valveId]={"roomId":room.get("id"), "roomName":room.get("Name")}
                else:
                    _LOGGER.warning(" Room doesnt contain any smart valves, maybe an error/corruption ")
        _LOGGER.debug(" valve2roomMap{} ".format(self.device2roomMap))
        return self.wiserHubData

        
    """
    retrieves the full JSON payload , for functions where I havent provided a API yet
    """
    def getHubData(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData
    def getRooms(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("Room")
    def getRoom(self,roomId):
        if (self.wiserHubData==None):
            self.refreshData()
        for room in (self.wiserHubData.get("Room")):
            if (room.get("id")==roomId):
                return room
        return None
    def getSystem(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("System")

    def getHotwater(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("HotWater")


    def getDevices(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("Device")

    def getDevice(self,deviceId):
        if (self.wiserHubData==None):
            self.refreshData()
        for device in (self.wiserHubData.get("Device")):
            if (device.get("id")==deviceId):
                return device
        return None

    """
    Convinience function to return the name of a room which is associated with a device (roomstat or trf)
    """
    def getDeviceRoom(self,deviceId):

        _LOGGER.debug(" getDeviceRoom called, valve2roomMap is {} ".format(self.device2roomMap))
        if not self.device2roomMap:
            self.refreshData()
        return self.device2roomMap[deviceId]

    # Get hot water status (On/Off)
    def getHeatingRelayStatus(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("HeatingChannel")[0].get("HeatingRelayState")
    
    # Get hot water status (On/Off)
    def getHotwaterRelayStatus(self):

        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("HotWater")[0].get("WaterHeatingState")
    
    # Get specific  dataSet for a roomStat
    def getRoomStatData(self,deviceId):
        if (self.wiserHubData==None):
            self.refreshData()
        for roomStat in self.wiserHubData['RoomStat']:
            if roomStat.get("id")==deviceId:
                return roomStat
        return None 
        
  

