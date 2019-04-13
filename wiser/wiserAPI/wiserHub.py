"""
Wiser API Facade

Currently embedded in the Home Assistant API but will be split into PyPi

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

import logging
import requests

_LOGGER = logging.getLogger(__name__)
WISERHUBURL = "http://{}/data/domain/"
WISERMODEURL= "http://{}/data/domain/System/RequestOverride"
WISERSETROOMTEMP= "http://{}//data/domain/Room/{}"
WISERROOM="http://{}//data/domain/Room/{}"


class wiserHub():
   

    def __init__(self,hubIP,secret):
        _LOGGER.info("WiserHub API Init")
        self.wiserHubData=None
        self.hubIP=hubIP
        self.hubSecret=secret
        self.headers = {'SECRET': self.hubSecret,'Content-Type': 'application/json;charset=UTF-8'}
        self.device2roomMap={}      # Dict holding Valve2Room mapping convinience variable
        self.refreshData()          # Issue first refresh in init
        
    def refreshData(self):
        smartValves=[]
        _LOGGER.info("Updating Wiser Hub Data")
        self.wiserHubData = requests.get(WISERHUBURL.format(
            self.hubIP), headers=self.headers).json()
        _LOGGER.debug("Wiser Hub Data received {} ".format(self.wiserHubData))
        if self.getRooms()!=None:
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
                    _LOGGER.warning(" Room doesnt contain any smart valves, maybe an error/corruption?? ")
            _LOGGER.debug(" valve2roomMap{} ".format(self.device2roomMap))
        else:
            _LOGGER.warning("Wiser found no rooms")
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
        if (self.wiserHubData.get("Room")==None):
            _LOGGER.warning("getRoom called but no rooms found")
            return None
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

    def getHeatingChannels(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("HeatingChannel")

    def getDevices(self):
        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("Device")

    def getDevice(self,deviceId):
        if (self.wiserHubData==None):
            self.refreshData()
        if (self.wiserHubData.get("Device")==None):
            _LOGGER.warning("getRoom called but no rooms found")
            return None
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
        heatingRelayStatus="Off"
        # There could be multiple heating channels, 
        heatingChannels=self.getHeatingChannels()
        for heatingChannel in heatingChannels:
            if heatingChannel.get("HeatingRelayState")=="On":
                heatingRelayStatus="On"
        return heatingRelayStatus
    
    # Get hot water status (On/Off)
    def getHotwaterRelayStatus(self):

        if (self.wiserHubData==None):
            self.refreshData()
        return self.wiserHubData.get("HotWater")[0].get("WaterHeatingState")
    
    # Get specific  dataSet for a roomStat
    def getRoomStatData(self,deviceId):
        if (self.wiserHubData==None):
            self.refreshData()
        if (self.wiserHubData['RoomStat']==None):
                _LOGGER.warning("getRoom called but no rooms found")
                return None
        for roomStat in self.wiserHubData['RoomStat']:
            if roomStat.get("id")==deviceId:
                return roomStat
        return None 

    # Set HomeAwayMode
    def setHomeAwayMode(self,mode,temperature=10):
        _LOGGER.info("Setting Home/Away mode to : {} {} C".format(mode,temperature/100))
        self.response=""
        self.patchData={}
        if (mode not in ['HOME','AWAY']):
            raise Exception("setAwayHome can only be HOME or AWAY")
        if (mode=="AWAY" and temperature!=None and (temperature <0 or temperature>400)):
              raise Exception("setAwayHome temperature can only be between 0 and 400 (100=10C)")
        print("Setting Home/Away : {}".format(mode))
        if (mode=="AWAY"):
            self.patchData={"type":2,"setPoint":temperature}
        else:
            self.patchData={"type":0,"setPoint":0}
        _LOGGER.debug ("patchdata {} ".format(self.patchData))
        self.response = requests.patch(url=WISERMODEURL.format(self.hubIP), headers=self.headers,json =self.patchData )
        # Strangely the response is always 403, but it works.. very strange..
        if (self.response.status_code!=403):
            _LOGGER.debug("Set Home/Away Response code = {}".format(self.response.status_code))
            raise Exception("Error setting Home/Away , error {} ".format(self.response.text))

    # Set Room Temperature
    def setRoomTemperature(self, roomId, temperature):
        _LOGGER.info("Set Room {} Temperature to = {} ".format(roomId,temperature))
        if (temperature<1 or temperature>40):
            raise Exception("SetRoomTemperature : value of temperature must be between 1 and 40")

        # the temp needs to be a whole number, so e.g. 19.5 -> 195
        apitemp = (str(temperature)).replace('.', '')
        patchData={"RequestOverride":{"Type":"Manual","SetPoint":apitemp}}
        self.response = requests.patch(WISERSETROOMTEMP.format(
            self.hubIP,roomId), headers=self.headers,json=patchData)
        
        if self.response.status_code != 200:
            _LOGGER.error("Set Room {} Temperature to = {} resulted in {}".format(roomId,temperature,self.response.status_code))
            raise Exception("Error setting temperature, error {} ".format(self.response.text))
        _LOGGER.debug("Set room Temp, error {} ({})".format(self.response.status_code, self.response.text))

    #Set Room Mode (Manual, Boost or Auto)
    def setRoomMode(self,roomId, mode,boost_temp=20,boost_temp_time=30):
        # TODO
        _LOGGER.debug("Set Mode {} for a room {} ".format(mode,roomId))
        if (mode.lower()=="auto"):
            #Do Auto
            patchData= {"Mode":"Auto"}
        elif (mode.lower()=="boost"):
            temp=boost_temp*10
            _LOGGER.debug("Setting Boost Temp to {}".format(temp))
            patchData={"RequestOverride":{"Type":"Manual","DurationMinutes": boost_temp_time, "SetPoint":temp, "Originator":"App"}}
        elif (mode.lower()=="manual"):
            patchData={"Mode":"Manual"} 
        else:
            raise Exception("Error setting setting room mode, received  {} but should be auto,boost or manual ".format(mode))
        
        # if not a boost operation cancel any current boost
        if (mode.lower()!="boost"):
            cancelBoostPostData={"RequestOverride":{"Type":"None","DurationMinutes": 0, "SetPoint":0, "Originator":"App"}}
            
            self.response = requests.patch(WISERROOM.format(self.hubIP,roomId), headers=self.headers,json=cancelBoostPostData)
            if (self.response.status_code != 200):
                _LOGGER.error("Cancelling boostresulted in {}".format(self.response.status_code))
                raise Exception("Error cancelling boost {} ".format(mode))
        # Set new mode
        self.response = requests.patch(WISERROOM.format(
            self.hubIP,roomId), headers=self.headers,json=patchData)        
        if self.response.status_code != 200:
            _LOGGER.error("Set Room mode to {} resulted in {}".format(mode,self.response.status_code))
            raise Exception("Error setting mode to error {} ".format(mode))
        

    
    

