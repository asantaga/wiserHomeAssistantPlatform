# Wiser Home Assistant Platform (v1.9)

This repository contains a Home Assistant component + platforms, for the awesome Drayton Wiser Heating solution.

Checkout `dev` branch for bleeding edge

## Functionality 

- Support for [Home Assistant Component Store](https://community.home-assistant.io/t/custom-component-hacs/121727)

- Support for Wiser TRVs, Hub and SmartPlugs

- **Climate platforms**
  
    - List of climate entities for each Room
    - Animated icons for the Rooms to let you know which rooms are actually being heated (credit @msp1974)
    - Allows setting of temperatures from HA
    - Allows setting of boost temperature using Home Assistant Presets
    - Displays icon if radiator is heating (heat flowing) or not
- **Service to set heating boost**
  
    - Services to get, set and copy heating schedules (See instructions below)**
    
- **Switch platform(s)**
  
   - Allows the switching of various system switches including EcoMode, ComfortMode, AwayMode, Valve Protection and AwayModeAffectsWater   
   - Allows the switching of the wiser system smartplugs
   
- **Sensor Platforms**
  
    - TRV Sensor
        - Each TRV is represented by a Sensor platform. Many attributes are exposed including extensive information about the device, such as WIFI Signal strength, firmware version, battery levels and zigbee information (including if connection to hub is direct or via repeater) etc
    - Room Thermostats Sensors 
        - Displayed attributes include battery levels, humidity etc
    - Smartplug displayed as a sensor, firmware etc
        - Service providing ability to turn smartplug on, off or set to auto schedule 
    - Heathub sensor
        - Attributes include zigbee channel , see https://support.metageek.com/hc/en-us/articles/203845040-ZigBee-and-WiFi-Coexistence for information on how zigbee and WIFI co-exist
    - Drayton Wiser Cloud Status Sensor 
        - Nice to be able to have automation when things aren't working
    - Heating Relay status Sensor 
        - Nice to know when the heating is on/off. 
          - This is nice to use in conjunction with the Climate platform when graphing data using Grafana
    - Hot Water relay status Sensor
        - Nice to know when the hot water is on/off. 
        - Also a service which allows you to modify the state of the hotwater 
    - Operation Mode Sensor (aka away sensor)
        - This sensor returns the away status of the heathub, being either `away` or `normal`. 
    
- **Services**

    - Following services are available for use with automation
    - Service `boost_heating` : Provides ability to boost the heating in a particular room
    - Service `get_schedule/set_schedule`: Provides ability to get/set schedules for rooms (not supported for smartplugs yet)
    - Service `set_smartplug_mode`: Provides ability to set the mode of a specific smartplug. It can be set to either `manual` or `auto` , the latter means it follows any schedule set.
        - NB : Setting the smartplug "state" is done by setting the state of the switch component.
    - Service `set_hotwater_mode`: Provides ability to turn a hot water **on**/**off** or **auto**. Valid values include `on`, `off` or `auto` Setting it to auto makes it follow the current schedule

- Support for Heathubs with No Hot Water Control 

- Fully async operation

    

    ## Sample Images

![](https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/docs/homeassistant_sample.jpg)


# Code Installation

We highly recommend using [HACS Home Assistant Community Store](https://github.com/hacs), for more information on how to install HACS please see their documentation website at https://hacs.xyz/



## Manual Code Installation

This method is best used when you want to play with the "latest and greatest" from the repository. Moving forward (post 1.9) , the github repository will contain two primary branches, **master** and dev. Master is the latest released, and hopefully most stable branch, whereas **dev** is the branch that we're currently working on.


1. On your server clone the github repository into a suitable directory using the following command
   git clone https://github.com/asantaga/wiserHomeAssistantPlatform.git

2. Switch to either the master or dev branch as per your requirements. 
   e.g.

   `git checkout master      `

   or 
   `git checkout dev`

3. Create a `custom_components` directory within your Home Assistant directory config directory

4. Within the custom components directory copy the wiser folder, from the directory where you github cloned the wiser component, to your installations ```custom components``` directory.


# Configuration


## Find your HeatHub Secret key
Reference https://it.knightnet.org.uk/kb/nr-qa/drayton-wiser-heating-control/#controlling-the-system

Before you can use the component you need to find the HeatHub secret key, this involves a couple of steps.


1. Press the setup button on your HeatHub, the light will start flashing

2. Look for the Wi-Fi network (SSID) called **‘WiserHeatXXX’** where XXX is random

3. Connect to the network from a Windows/Linux/Mac machine

4. Execute the following REST call 
   * For Windows use
      `Invoke-RestMethod -Method Get -UseBasicParsing -Uri http://192.168.8.1/secret/` 
   * For Linux (or Windows WSL) use 
     `curl http://192.168.8.1/secret`


   This will return a string which will contain your system secret, obviously dont share this...

5. Press the setup button on the HeatHub again and it will go back to normal operations

6. Copy the secret and save it somewhere.

7. Find Your HEATHUB IP
    Using your router, or some other method, identify the IP address of your HeatHub. On many routers it usually identifies itself as the something like ``WiserHeatXXXXXX`` 

8. Add references to Home Assistant `Configuration.yaml` file 

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

I don't recommend you set the scan_interval too low, after all temperatures do not change that often and 300 seconds(5mins) is probably plenty but adjust as per your requirements.

```minimum``` is the bottom minimum temperature to be recorded, the default is -5

```boost_temp``` is the delta temperature the radiator should be set to when boosted, default is 2

```boost_time``` is the time (in seconds) for which a boost should be active for, default is 30mins




## Managing Schedules with Home Assistant

### Getting a Schedule
Use the service `wiser.get_schedule`

This will require you to provide the entity ID of the wiser device and a file to copy this schedule to.
It is recommended to create a directory in your config directory to store these.

### Setting a Schedule
Use the service `wiser.set_schedule`

This will require you to provide the entity ID of the wiser device and a file containing the schedule.

A good place to start is to get a schedule from a device and see the file structure.  You can add times and temps within each day as you see fit.  As file created using the wiser.get_schedule service looks like below:
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
names of 'Weekdays' and 'Weekends' instead of listing individual days.  

e.g.

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
You can also use a mixture of these special day names and normal days to override a specific day (providing the specific days names are below these special ones!).
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
Use the service `wiser.copy_schedule`

This will require you to provide an entity ID of the device to copy from and the entity ID of the device to copy toand will copy the schedule between them.

## Network Topology

With V1.9 for TRVs you can now determine if the TRV is connected to the heathub directly or via a smartplug repeater. 

Each TRV sensor now has three special network related attributes 

| Attribute        | Meaning                                                      |
| ---------------- | ------------------------------------------------------------ |
| `node_id`        | The node Id of the device                                    |
| `parent_node_id` | If this value is zero (0) then the device is connected direct to the heathub. A non zero value points to the smartplug/repeater for which this device is being routed through. Smartplugs always have this value as zero |
| `hub_route`      | Calculated convenience attribute which the evaluates to either `direct` or `repeater` based on if the device is connected direct or not to the heathub |



## Battery Values

For each battery driven device sensor the following attributes are available `battery_voltage`, `battery_percentage` and `battery_level`. From conversations with Wiser technical support they recommend changing the batteries for any TRV when it reaches battery voltage of "26" or OneThird battery level. RoomStats battery levels can be lower.

An obvious ideal candidate for a Home Assistant automation to remind you to change the batteries :-)

Note : If you power cycle your HomeHub, with more than a minute or so when it is off, we've noticed that the devices will not have the battery info for a short period of time (maybe 30mins to 1hr). 



# Run, Play 

***Run, Play*** and let us know if there are any bugs, enhancements etc via the github issues system

Special thanks for many contributors to this project!

Angelo

# Contributors

Special thanks to all the contributors to this project.  Special shout to 

- @angrycamel  : Home/Away Sensor
- @jchasey     : Doc changes and support for custom component updater
- @sjtbham     : Debugging
- @djbanks     : Home/Away switch (v 1.31)
- @msp1974     : Animated graphics showing which rooms are being heated, Display Presets, support boost (PR38), Async Mode rewrite and loads more!



Moving forward (post 1.9) there will be two primary branches, `master` and `dev` . Master will be the primary "production" branch and "dev" will be the branch used for development. Other branches will likely exist where we build code into and then merge into dev, which in turn gets merged into master when all is good and dandy.

# Change log
- 1.9      
  
    * Component rewritten to use Async to ensure the component is more robust and HA friendly
    
    * Ability to control SmartPlugs
    
    * Zigbee Network info now available
    
    * Ability to control hotwater (using a service)
    
    * Ability to get/set schedule using services 
    
    * Ability to set/get system settings , like auto mode, eco mode etc
    
    * and Many more
    
    
      **BREAKING CHANGE** : We no longer support the custom component updater, please use HACS instead
    
- 1.8.1	   
  
    * Multiple fixes to timeouts, boost and upgrade to wiserapi 1.0.3
- 1.7      
    * Presets and now supports delta boosts (thanks @msp1974)
    * BREAKING CHANGE : boost temp is now a delta and not a specific value  e.g.. now is 2C vs previously 20C
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
    * Fix bug where updates weren't seen till new refresh cycle
    * Changes to make code HA native component compatible (more work to be done)
- 1.3.1    
  
    * Merged djbanks Home/Away switch
- 1.3
    * Added ability to set temperature
    * Added ability to set room mode (auto,boost,manual)
