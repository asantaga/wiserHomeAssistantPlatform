# Wiser Home Assistant Platform (v1.9Dev)

This repository contains a Home Assistant component + platforms, for the Drayton Wiser Heating solution.

## Functionality 

- Support for Custom components and HACS!!
- Climate platforms
    - List of climate entities for each Room. The state is the current temperature and the target temperature.  
    - Allows setting of temperatures from HA
    - Allows setting of boost temperature using Home Assistant Presets
    - Displays icon if radiator is heating (heat flowing) or not
    - Service to set heating boost
    - Services to get, set and copy heating schedules (**See instructions below**)

- Switch platform
   - Allows the switching of various system switches including EcoMode, ComfortMode, AwayMode, Valve Protection and AwayModeAffectsWater   
   - Allows the switching of the wiser system smartplugs
   
- Sensor Platforms
    - Each **TRV** is representated by a Sensor. The sensor attributes include extensive information about the device, such as WIFI Signal strength, firmware version, battery levels etc
    - **Heathub** displayed as a sensor, firmware version etc
    - **Smartplug** displayed as a sensor, firmware etc
    - **Room Thermostats** displayed as sensors
        - Additonal attributes include battery levels, humidity etc
    - Drayton **Wiser Cloud** Status
        - Nice to be able to have automation when things aren't working
    - Heating Relay status
        - Nice to know when the heating is on/off. This is nice to use in conjunction with the Climate platform when graphing data using grafana
    - Hot Water relay status
        - Nice to know when the hot water is on/off. 
    - Full access to the JSON payload from the HeatHub, for those things I didn't think of... 
    - Support for Heathubs with No Hot Water Control (added 1.1)
    - Support for Home/Away Sensor (added v1.1)
    - Support for setting room mode (boost/manual/auto) (added in 1.3)
    - Animated icons for the Rooms to let you know which rooms are actually being heated (@msp1974)


## Sample Images

![](https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/docs/homeassistant_sample.jpg)


# Code Installation

For the software side of things we now support  [custom_updater](https://github.com/custom-components/custom_updater)  updater OR [HACS Home Assistant Community Store](https://github.com/hacs). 
Use either one to install the component the go for configuration. using HACS or Custom Updater means you will automagically get updates when I release them.

I *highly recommend HACS*, for instructions on how to install HACS see their documentation website at https://hacs.xyz/

## For custom_updater

Add this to your configuration:
```yaml
custom_updater:
  component_urls:
    - https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/custom_components.json
```

## For HACS (Recommended)
See installation instructions at the HACS documentation website https://hacs.xyz/


## Manual Code Installation


1. Create a `custom_components` directory within your Home Assistant directory
2. In a different directory clone the git repositry https://github.com/asantaga/wiserHomeAssistantPlatform.git
3. Within this directory copy the wiser folder (within custom_components) to your installations ```custom components``` directory


# Configuration


## Find your HeatHub Secret key
Reference https://it.knightnet.org.uk/kb/nr-qa/drayton-wiser-heating-control/#controlling-the-system
1. Press the setup button on your HeatHub, the light will start flashing
Look for the Wi-Fi network (SSID) called **‘WiserHeatXXX’** where XXX is random
2. Connect to the network from a Windows/Linux/Mac machine
3. Execute the secret url :-)
   * For Windows use `Invoke-RestMethod -Method Get -UseBasicParsing -Uri http://192.168.8.1/secret/` 
   * For Linux (or Windows WSL) use `curl http://192.168.8.1/secret`

   This will return a string which is your system secret

4. Press the setup button on the HeatHub again and it will go back to normal operations
5. Copy the secret and save it somewhere.
6. Find Your HEATHUB IP
Using your router, or something else, identify the IP address of your HeatHub, it usually identifies itself as the same ID as the ``WiserHeatXXXXXX`` 

7. Add references to Home Assistant `Configuration.yaml` file 

Here is a sample config, replace the HEATHUB AND PASSWORD appropriately.
```
wiser:
  host: <ENTER YOUR HEATHUB IP HERE>
  password: <ENTER YOUR SECRET TOKEN, OBTAINED FROM STEP THREE HERE>
  scan_interval: 300
  minimum: -5
  boost_temp: 2
  boost_time: 30
```

I don't recommend you set the scan_interval too low, after all temperatures do not change that often and 300 seconds(5mins) is probably plenty.
```minimum``` is the bottom minimum temperature to be recorded, the default is -5

```boost_temp``` is the delta temperature the radiator should be set to when boosted, default is 2

```boost_time``` is the time (in seconds) for which a boost should be active for, default is 30mins


# Managing Schedules with HA

New in version 1.x is the ability to get, set and copy schedules from climate devices.

### Getting a Schedule
Use the service wiser.get_schedule.
This will require you to provide the entity ID of the wiser device and a file to copy this schedule to.
It is recommended to create a directory in your config directory to store these.

### Setting a Schedule
Use the service wiser.set_schedule.
This will require you to provide the entity ID of the wiser device and a file containing the schedule.

A good place to start is to get a schedule from a device and see the file structure.  You can add times and temps within
each day as you see fit.  As file created using the wiser.get_schedule service looks like below:
```
Name: Dining Room
Description: Schedule for Dining Room
Type: Heating
Monday:
  - Time: 07:30
    Temp: 21
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Tuesday:
  - Time: 07:30
    Temp: 21
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Wednesday:
  - Time: 07:30
    Temp: 21
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Thursday:
  - Time: 07:30
    Temp: 21
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Friday:
  - Time: 07:30
    Temp: 21
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Saturday:
  - Time: 07:00
    Temp: 19
  - Time: 10:00
    Temp: 17
  - Time: 16:00
    Temp: 20
  - Time: 23:00
    Temp: 15
Sunday:
  - Time: 08:30
    Temp: 21
```
If you are creating your own file (or editing one you have copied from a wiser device), you can use the 2 special day
names of 'Weekdays' and 'Weekends' instead of listing individual days.  As below:
```
Name: Test Room
Description: Schedule for Test Room
Type: Heating
Weekdays:
  - Time: 07:30
    Temp: 21.5
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Weekends:
  - Time: 07:00
    Temp: 19
  - Time: 10:00
    Temp: 17
  - Time: 16:00
    Temp: 20.5
  - Time: 23:00
    Temp: 15
```
You can also use a mixture of these special day names and normal days to override a specific day (providing the
specific days names are below these special ones!).
```
Name: Test Room
Description: Schedule for Test Room
Type: Heating
Weekdays:
  - Time: 07:30
    Temp: 21.5
  - Time: 08:30
    Temp: 15
  - Time: 16:30
    Temp: 20
  - Time: 22:30
    Temp: 15
Weekends:
  - Time: 07:00
    Temp: 19
  - Time: 10:00
    Temp: 17
  - Time: 16:00
    Temp: 20.5
  - Time: 23:00
    Temp: 15
Tuesday:
  - Time: 08:00
    Temp: 21.5
  - Time: 20:00
    Temp: 18.0
```

### Copying a Schedule
Use the service wiser.copy_schedule.
This will require you to provide an entity ID of the device to copy from and the entity ID of the device to copy to
and will copy the schedule between them.

------

***Run, Play*** and let us know if there are any bugs, enhancements etc via the github issues system

Special thanks for contributors 
Thanks!

Angelo and the many contributors to this project!

# Contributors

- @angrycamel  : Home/Away Sensor
- @jchasey     : Doc changes and support for custom component updater
- @sjtbham     : Debugging
- @djbanks     : Home/Away switch (v 1.31)
- @msp1974     : Animated graphics showing which rooms are being heated 
                 Display Presets and support boost (PR38)
                 Async Mode rewrite
                 Loads more!

# Change log
- 1.9      
    * Component rewritten to use Async, Displayed Setpoint bug fixed for eco mode
    * Ability to control SmartPlugs
           
- 1.8.1	   
    * Multiple fixes to timeouts, boost and upgrade to wiserapi 1.0.3
- 1.7      
    * Presets and now supports delta boosts (thanks @msp1974)
    * BREAKING CHANGE : boost temp is now a delta and not a specific value  e.g. now is 2C vs previously 20C
- 1.6.1    
    * Fixed setting temperature bugs 
- 1.6      
    * Merged functionality where it now shows which rooms are being heated by an icon 
- 1.5.1    
    * Minor bump to fix home/away issue and bring versions inline
- 1.5 	   
    * Now supports HACS
- 1.4      
    * Major changes. Now uses pypi library 
    * Uses new Climate Model (see https://developers.home-assistant.io/blog/2019/07/03/climate-cleanup.html)
    * Fix bug where updates werent seen till new refresh cycle
    * Changes to make code HA native component compatible (more work to be done)
- 1.3.1    
    * Merged djbanks Home/Away switch
- 1.3
    * Added ability to set temperature
    * Added ability to set room mode (auto,boost,manual)
