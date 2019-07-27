# Wiser Home Assistant Platform (v1.5.0)


This repository contains a Home Assistant component + platforms, for the Drayton Wiser Heating solution.

This component provides the following functionality :

- Support for Custom components and HACS!!
- Climate platforms
    - List of climate entities for each Room. The state is the current temperature and the target temperature.  
- Switch platform
   - Allows the switching of Home/Away mode via a switch which means it can now be controlled by HA
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



## Sample Images

![](https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/docs/homeassistant_sample.jpg)


# Code Installation

For the software side of things we now support  [custom_updater](https://github.com/custom-components/custom_updater)  updater OR [HACS](https://custom-components.github.io/hacs/). 
Use either one to install the component the go for configuration. using HACS or Custom Updater means you will automagically get updates when I release them.

## For custom_updater

Add this to your configuration:
```yaml
custom_updater:
  component_urls:
    - https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/custom_components.json
```

## For HACS
Install via dashboard or add github repository manually


## Manual Code Installation


1. Create a `custom_components` directory within your Home Assistant directory
2. In a different directory clone the git repositry https://github.com/asantaga/wiserHomeAssistantPlatform.git
3. Within this directory copy the wiser folder (within custom_components) to your installations ```custom components``` directory


# Configuration


## 1. Find your HeatHub Secret key
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
  boost_temp: 20
  boost_time: 30
```

I don't recommend you set the scan_interval too low, after all temperatures do not change that often and 300 seconds(5mins) is probably plenty.
```minimum``` is the bottom minimum temperature to be recorded, the default is -5

```boost_temp``` is the temperature the radiator should be set to when boosted, default is 20

```boost_time``` is the time (in seconds) for which a boost should be active for, default is 30mins

------

***Run, Play*** and let me know if there are any bugs, enhancements etc via the github issues system

Special thanks for contributors 
Thanks!

Angelo

# Contributors

- @angrycamel  : Home/Away Sensor
- @jchasey     : Doc changes and support for custom component updater
- @sjtbham     : Debugging
- @djbanks     : Home/Away switch (v 1.31)

# Change log
- 1.5 	   Now supports HACS
- 1.4      Major changes. Now uses pypi library 
           Uses new Climate Model (see https://developers.home-assistant.io/blog/2019/07/03/climate-cleanup.html)
           Fix bug where updates werent seen till new refresh cycle
           Changes to make code HA native component compatible (more work to be done)
- 1.3.1    Merged djbanks Home/Away switch
- 1.3      Added ability to set temperature
           Added ability to set room mode (auto,boost,manual)


