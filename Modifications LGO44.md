# wiserLightsShutters
  Developpment of lights and shutters for the wiserHomeAssistantPlatform

Developped by LGO44 with the help of Mark Parker 
based on 
climate.py for light.py and cover.py 


## Process
 Fork the dev branch of the repository 

 paste the filof my modification in my local repository

- heatingactuators: 
    I have also added 2 sensors for the energy management in the sensor.py

- lights and shutters:
	For light and shutters 

## files
  /translations/fr.json
  const.py
  light.py
  cover.py
  select.py
  helpers.py
  sensor.py
  switch.py
  climate.py
  service.yaml

### My modifications

* a fr.json for the translation in french of the settings of the WiserHub

* const.py 
    ** add "light" and "cover" in the WISER_PLATFORMS

* light.py and cover.py 

* select.py:
    ** add 2 selectors for wiserlightmodeselect wisershuttermodeselect 
    ** 2 services to set mode for light and shutter
    ** 2 classes WiserLightModeSelect,  WiserShutterModeSelect  

* helpers.py :
    modify the naming of the lights and shutters 

* sensor.py
    ** creation of 2 LTS sensor for energy management for the heatings actuators
    ** add of attributes

* Switch.py
    ** creation of 2 actionswitch for away_action_modes _turn_off for light an shutter
        class WiserLightAwayActionSwitch and class WiserShutterAwayActionSwitch
    ** based on the smartplug I have created 2 other switch (put in comment) the classesclass WiserLightSwitch and class WiserShutterSwitch are not called  ( can be erased) 

* Climate.py
    ** add several properties and attributes      

* Service.yaml
    ** 2 service to selecte the mode of light and shutter

