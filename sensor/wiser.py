"""
Sensor Platform Device for Wiser System


https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com

"""
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.const import (
    CONF_ENTITY_NAMESPACE,
    STATE_UNKNOWN, ATTR_ATTRIBUTION)

_LOGGER = logging.getLogger(__name__)
DOMAIN = "wiser"
BATTERY_FULL =31



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    handler = hass.data[DOMAIN] # Get Handler
    hubData = handler.getHubData()
    handler.update()
    wiserDevices= []
    # Process  general devices
    for device in handler.getHubData().getDevices():
        wiserDevices.append(WiserDevice(device.get('id'),handler,device.get("ProductType")))
    wiserDevices.append(WiserSystemCircuitState(handler,"HEATING")   )
    wiserDevices.append(WiserSystemCircuitState(handler,"HOTWATER")   )
    wiserDevices.append(WiserSystemCloudSensor(handler))
    wiserDevices.append(WiserSystemOperationModeSensor(handler))
    add_devices(wiserDevices)
    

""" 
Definition of Wiser Device
"""
class WiserDevice(Entity):
    def __init__(self, deviceId,handler,sensorType):
            
        """Initialize the sensor."""
        _LOGGER.info('Wiser Device Init')
      
        self.handler=handler
        self.deviceId=deviceId
        self.sensorType=sensorType

    def update(self):
        _LOGGER.debug('**********************************')
        _LOGGER.debug('Wiser Device Update requested')
        _LOGGER.debug('**********************************')
        self.handler.update()

    @property
    def icon(self):
        iconList={
                'Poor':'mdi:wifi-strength-1',
                'Medium':'mdi:wifi-strength-2',
                'Good':'mdi:wifi-strength-3',
                'VeryGood':'mdi:wifi-strength-4'
                }
        try:
            return iconList[self.handler.getHubData().getDevice(self.deviceId).get("DisplayedSignalStrength")]
        except KeyError as ex:
            # Handle anything else as no signal
            return 'mdi:wifi-strength-alert-outline'

    @property
    def name(self):
        #Return the name of the Device
        productType=str(self.handler.getHubData().getDevice(self.deviceId).get("ProductType") or '')

        if (productType=="Controller"):
            return "Wiser Heathub"  # Only ever one of these
        elif (productType=="iTRV"):
            return "Wiser "+productType + "-"+ self.handler.getHubData().getDeviceRoom(self.deviceId)['roomName'] # Multiple ones get automagically number _n by HA
        
        elif (productType=="RoomStat"):
            return "Wiser "+productType + "-"+ self.handler.getHubData().getDeviceRoom(self.deviceId)['roomName'] # Usually only one per room
        else:
            return "Wiser "+productType +"-"+ str(self.handler.getHubData().getDevice(self.deviceId).get("SerialNumber") or '')
 
    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    #Assumption 31 = 100% battery
    @property
    def battery_level(self):
        return self.handler.getHubData().getDevice(self.deviceId).get("BatteryVoltage")/BATTERY_FULL*100
    
    @property
    def device_state_attributes(self):
        _LOGGER.debug('State attributes for {} {}'.format(self.deviceId,self.sensorType))

        attrs={}
        deviceData=self.handler.getHubData().getDevice(self.deviceId)
        # Generic attributes
        attrs['vendor'] = "Drayton Wiser"
        attrs['product_type']=deviceData.get("ProductType")
        attrs['model_identifier'] = deviceData.get("ModelIdentifier")
        attrs['device_lock_enabled'] = deviceData.get("DeviceLockEnabled")
        attrs['displayed_signal_strength'] = deviceData.get("DisplayedSignalStrength")
        attrs['firmware'] = deviceData.get("ActiveFirmwareVersion")

        if deviceData.get("ReceptionOfDevice")!=None:
            attrs['device_reception_RSSI'] = deviceData.get("ReceptionOfDevice").get("Rssi")
            attrs['device_reception_LQI'] = deviceData.get("ReceptionOfDevice").get("Lqi")
            
        
        if deviceData.get("ReceptionOfController")!=None:
            attrs['controller_reception_RSSI'] = deviceData.get("ReceptionOfController").get("Rssi")
            attrs['device_reception_LQI'] = deviceData.get("ReceptionOfController").get("Lqi")
            
        if self.sensorType in ['RoomStat','iTRV','SmartPlug']:
            attrs['battery_voltage']=deviceData.get("BatteryVoltage")
            attrs['battery_level']=deviceData.get("BatteryLevel")
            attrs['serial_number']=deviceData.get("SerialNumber")

        if self.sensorType=='RoomStat':
            attrs['humidity']=self.handler.getHubData().getRoomStatData(self.deviceId).get('MeasuredHumidity')
        return attrs
    @property
    def state(self):
        _LOGGER.debug('**********************************')
        _LOGGER.debug('Wiser Device state requested deviceId : %s',self.deviceId)
        _LOGGER.debug('**********************************')
        return self.handler.getHubData().getDevice(self.deviceId).get("DisplayedSignalStrength")
        

""" 
Specific Sensor to display the status of heating or water circuit
"""
class WiserSystemCircuitState(Entity):
    # circuitType is HEATING HOTWATER
    def __init__(self,handler,circuitType):
            
        """Initialize the sensor."""
        _LOGGER.info('Wiser Circuit Sensor Init')
        self.handler=handler
        self.circuitType=circuitType

    def update(self):
        _LOGGER.debug('**********************************')
        _LOGGER.debug('Wiser Cloud Circut status Update requested')
        _LOGGER.debug('**********************************')
        self.handler.update()
    @property
    def icon(self):
        if self.circuitType=='HEATING':
            if self.state=="Off":
                return 'mdi:radiator-disabled'
            else:
                return "mdi:radiator"
        else:
            # HOT WATER
            if self.state=="Off":
                return 'mdi:water-off'
            else:
                return "mdi:water"

    @property
    def name(self):
        """Return the name of the Device """
        if self.circuitType=="HEATING":
            return "Wiser Heating"
        else:
            return "Wiser Hot Water"

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    
    @property
    def state(self):
        _LOGGER.debug('**********************************')
        _LOGGER.debug('Wiser Cloud Circut STATE requested')
        _LOGGER.debug('**********************************')
        if self.circuitType=="HEATING":
            return self.handler.getHubData().getHeatingRelayStatus()
        else:
            return self.handler.getHubData().getHotwaterRelayStatus()        
  

"""
Sensor to display the status of the Wiser Cloud
"""
class WiserSystemCloudSensor(Entity):
    def __init__(self,handler):
            
        """Initialize the sensor."""
        _LOGGER.info('Wiser Cloud Sensor Init')
        self.handler=handler
        self.cloudStatus=self.handler.getHubData().getSystem().get("CloudConnectionStatus")
      
    def update(self):
        _LOGGER.debug('Wiser Cloud Sensor Update requested')
        self.handler.update()
        self.cloudStatus=self.handler.getHubData().getSystem().get("CloudConnectionStatus")

    @property
    def icon(self):
        if self.cloudStatus =="Connected":
            return "mdi:cloud-check"
        else:
            return "mdi:cloud-alert"
    @property
    def name(self):
        """Return the name of the Device """
        return ("Wiser Cloud Status")

    @property
    def should_poll(self):
        """Return the polling state."""
        return True
    @property
    def state(self):
        _LOGGER.debug('**********************************')
        _LOGGER.debug('Wiser Cloud  status Update requested')
        _LOGGER.debug('**********************************')
        return self.cloudStatus
    
  
"""
Sensor to display the status of the Wiser Operation Mode (Away/Normal etc)
"""
class WiserSystemOperationModeSensor(Entity):
    def __init__(self,handler):
            
        """Initialize the sensor."""
        _LOGGER.info('Wiser Operation  Mode Sensor Init')
        self.handler=handler
        self.overrideType=self.handler.getHubData().getSystem().get("OverrideType")
        self.awayTemperature=self.handler.getHubData().getSystem().get("AwayModeSetPointLimit")
      
    def update(self):
        _LOGGER.debug('Wiser Operation Mode Sensor Update requested')
        self.handler.update()
        self.overrideType=self.handler.getHubData().getSystem().get("OverrideType")
        self.awayTemperature=self.handler.getHubData().getSystem().get("AwayModeSetPointLimit")

    def mode(self):
        if self.overrideType and self.overrideType == "Away":
            return "Away"
        else:
            return "Normal"

    @property
    def icon(self):
        if self.mode() == "Normal":
            return "mdi:check"
        else:
            return "mdi:alert"

    @property
    def name(self):
        """Return the name of the Device """
        return ("Wiser Operation Mode")

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def state(self):
        return self.mode()

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = { "AwayModeTemperature": -1.0 }
        if self.awayTemperature:
            try:
                attrs["AwayModeTemperature"] = int(self.awayTemperature)/10.0
                _LOGGER.debug("Used value for awayTemperature", self.awayTemperature)
            except:
                _LOGGER.debug("Unexpected value for awayTemperature", self.awayTemperature)
        return attrs

