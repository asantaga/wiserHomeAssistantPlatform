# Wiser Home Assistant Platform (v1.2)


This repository contains a Home Assistant component + platforms, for the Drayton Wiser Heating solution.

This component provides the following functionality
-Climate platforms
    - List of climate entities for each Room. The state is the current temperature and the target temperature.  
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

Currently the Component/Platform is read only, I do plan to add the ability to set the setpoints in the near future

## Sample Image

![](https://raw.githubusercontent.com/asantaga/wiserHomeAssistantPlatform/master/docs/homeassistant_sample.jpg)


# Installation
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
## 3. Find Your HEATHUB IP

Using your router, or something else, identify the IP address of your HeatHub, it usually identifies itself as the same ID as the ``WiserHeatXXXXXX`` 

## 3. Create a `custom_components` directory within your Home Assistant directory

For components which arent part of the official release yet (i said yet) you can put them into a directory called  custom components

## 4. Copy files 
From github to your Home Assistant custom_components directory. Easiest way is to issue a git clone to your local directory and then copy all the files to the custom_components directory
e.g. 
    ```git clone git@github.com:asantaga/wiserHomeAssistantPlatform.git```

This will usually create a directory called "wiserHomeAssistantPlatform", once done then copy the ```wiser``` directory into the custom_components directory

## 5. Add references to Home Assistant `Configuration.yaml` file 

Here is a sample config, replace the HEATHUB AND PASSWORD appropriately.

```
wiser:
  host: <ENTER YOUR HEATHUB IP HERE>
  password: <ENTER YOUR SECRET TOKEN, OBTAINED FROM STEP THREE HERE>
  scan_interval: 300
  minimum: -5
```

I don't recommend you set the scan_interval too low, after all temperatures do not change that often and 300 seconds(5mins) is probably plenty.
```minimum``` is the bottom minimum temperature to be recorded, the default is -5

## 6. Run, Play and let me know if there are any bugs, enhancements etc via the github issues system

Special thanks for contributors 
Thanks!

Angelo

# Contributors

- @angrycamel  : Home/Away Sensor
- @jchasey     : Doc changes
