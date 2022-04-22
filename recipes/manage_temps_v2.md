# Using External Temp Sensor to Manage Room Temp Accuracy V2

The basic premise of this automation is to monitor a series of external temperature sensors and boost wiser room heating to reach the correct temperature as set by the schedule, which is one of the failings of having the temp sensor in the iTRV as it is too close to the heat source to be truly accurate for a whole room and often shuts the heating off before the room is at the correct temp.

On updates from the external temp sensor, it will compare this to the scheduled temp of the Wiser climate device (aka room).  If the room is not already heating or boosted, it will boost the room by 1.5x (adjustable) the difference.  I have found this to give pretty good results but this may need tweaking for your own home.

It will also look if the current room temp is within 0.5C (adjustable) of the scheduled temp and cancel any boost if it is.

## There are 3 requirements for this automation to work:

1) You need at least version 3.0.20 of the Wiser integration for HA.  It uses the 'current scheduled temp' attribute that was new in this version.
2) You need at least v2022.4 of Home Assistant for the trigger variable functionality
3) That your temperature sensors are setup in HA Areas with the Wiser Climate device you wish to control in the same area.

## Changes in V2

### 1) Splitting Into 2 Automations
I originally tried to write this as a single automation (which worked fine) however I think it added quite a bit of overhead to HA as I could only trigger it on all state changes.  It was also very difficult to debug as each state change for any device triggered it and therefore traces contained triggers not for what I was interested in debugging.  As such, it is now split into 2 main parts.  
  - Part 1 (Fire Event When Room Monitoring Temp Sensors Change Reading) is the automation to monitor for temperature changes in the devices I am interested in and fire a customer event when a temperature change is registered.
  - Part 2 (Manage Wiser Heating From Ext Temp Sensor) is the automation, triggered by this custom event to find the Wiser Climate device in the same room as the temp sensor and boost/cancel boost where necessary.  It also logs key informaiton in the logbook so you can see when it has activated, what the schedule temp/sensor temp was, how much it boosted by etc and also when it cancelled a boost.

This 2 part method means that you can have different types of temperature sensors in different rooms and just repeat the Part 1 automation for each type of sensor without any changes or additional Part 2 automations needed.

### 2) Simplifying with New Trigger Variables
The V1 of this automation repeated a lot of code as there was no way to set variables in triggers - now there is!  So, I have used this new functionality and it has really simplified this down and made it much more readable.  You can now also adjust parameters simply to suit personal situation/need/desire etc.


## Setting Up This Automation

### 1) Setting Up Your Temp Sensors
- Firstly setup your temp sensors in HA and allocate them to Areas for your rooms.  Your Wiser climate entities must be in the same area as the temp sensor that it is associated with.
- Create the Fire Event When Room Monitoring Temp Sensors Change Reading automation by creating a new automation and copying the below YAML code.  You can call it whatever you want as this does not matter.
- In the Fire Event When Room Monitoring Temp Sensors Change Reading automation, you will need to adjust the following variables to suit your setup (the integration code below is using Aquara Zigbee sensors, so if you have the same, no changes needed)
  - **temp_sensor_integration** - this is the name of the integration that controls your temp sensor (eg zha)
  - **temp_sensor_prefix** - this is the prefix that all your sensors have (eg sensor.lumi). Differentiates between other sensor types from the integration
  - **temp_sensor_suffix** - this is the suffix that all your sensors have (eg: temperature).  Differntiates between humidity, temp, battery etc for multi sensor sensors

  **Notes:**
  - Adding new climate devices or temp sensors (providing they are of the same type you already have) should require no changes to this part of the automation.
  - If you want to add some different sensors (for another room for example), create another automation of this code and follow the same config instructions for your new sensor types

  ```yaml
  alias: Fire Event When Room Monitoring Temp Sensors Change Reading
  description: ''
  trigger:
    - platform: event
      event_type: state_changed
      variables:
        temp_sensor: '{{trigger.event.data.entity_id}}'
  condition:
    - condition: template
      value_template: |-
        {% if temp_sensor in integration_entities(temp_sensor_integration)
                and temp_sensor.startswith(temp_sensor_prefix) 
                and temp_sensor.endswith(temp_sensor_suffix)
        %}
          True
        {% endif %}
  action:
    - event: external_temp_sensor_changed
      event_data:
        entity_id: '{{temp_sensor}}'
        old_temp: '{{trigger.event.data.old_state.state}}'
        new_temp: '{{trigger.event.data.new_state.state}}'
  trigger_variables:
    temp_sensor_integration: zha
    temp_sensor_prefix: sensor.lumi
    temp_sensor_suffix: temperature
  mode: queued
  max: 25
  ```

### 2) Setting Up Room Boost
- Create the Adjust Wiser Boost for Ext Temp Sensor Heat Management automation by creating a new automation and copying the below YAML code.  You can call it whatever you want as this does not matter.
- There are a few configuration variables you can use to adjust how this performs but I have found the default values to work pretty well.  If you want to adjust them, below is a description of what they do:
    - **boost_time** - how long the automation will boost the temp for.  Note that when the temp sensor reads a temp within the tolerance to the scheduled temp, the automation will cancel the boost before it has hit this time.  I would only adjust it if the boost still does not get the room upto temp.  Also, think about more insulation in your house!
    - **tolerance_delta** - this is how much tolerance you allow between the temp sensor reported temp and the scheduled temp before it boosts the heating (or cancels the boost)
    - **max_boost_delta** - this is the max boost temp increase.  The hub will only do a maximum of 5C but you can reduce this if you want to only boost a max of 3C for example.
    - **non variable config option** - due to not being able to use trigger_variables within the tigger variable section, the multiplier used to determine the boost temp is hard coded.  See the boost_delta_temp variable in the line below.  You can adjust this 1.5 value to boost to higher or lower temps above the scheduled temp.  Depending on your heating system, a higher value will get the room up to temp quicker but may cause it to exceed the scheduled temp if the temp sensor does not report frequently enough to cancel the boost when temp reached.
    ```yaml
    boost_delta_temp: '{{(((current_temp_delta * 1.5) * 2 )|round(0)/2)|round(1)}}'
    ```
    


  ```yaml
  alias: Adjust Wiser Boost for Ext Temp Sensor Heat Management
  description: Uses External Temp Sensor To Achieve Target Temp in Room
  trigger:
    - platform: event
      event_type: external_temp_sensor_changed
      variables:
        temp_sensor: '{{trigger.event.data.entity_id}}'
        temp_sensor_temp: '{{trigger.event.data.new_temp}}'
        climate_entity: |-
          {% for wiser_climate in area_entities(area_name(temp_sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser')
          %}
            {% if loop.first %}
              {{wiser_climate}}
            {% endif %}
          {% endfor %}
        schedule_temp: '{{state_attr(climate_entity, "current_schedule_temp")|float(0)}}'
        current_temp_delta: '{{(schedule_temp - temp_sensor_temp)|round(1)}}'
        boost_delta_temp: '{{(((current_temp_delta * 1.5) * 2 )|round(0)/2)|round(1)}}'
  condition:
    - condition: and
      conditions:
        - condition: template
          value_template: '{{ states(climate_entity) is defined }}'
        - condition: template
          value_template: |-
            {% if (
                  current_temp_delta > tolerance_delta
                  and not state_attr(climate_entity, 'is_heating')
                  and not state_attr(climate_entity, 'is_boosted')
                )
                or
                (
                  current_temp_delta < tolerance_delta 
                  and state_attr(climate_entity, 'is_boosted')
                )
            %}
                True    
            {% endif %}
  action:
    - service: wiser.boost_heating
      data_template:
        entity_id: '{{climate_entity}}'
        time_period: '{{ 0 if current_temp_delta < tolerance_delta else boost_time }}'
        temperature_delta: >-
          {{ 0 if current_temp_delta < tolerance_delta else [boost_delta_temp,
          max_boost_delta]|min}}
    - service: logbook.log
      data_template:
        name: Wiser Temp Boost by Ext Sensor
        message: |-
          Temp Sensor - {{temp_sensor}},
          Temp Sensor Temp - {{temp_sensor_temp}}°C, 
          Climate Entity - {{climate_entity}},
          Schedule Temp - {{schedule_temp}}°C, 
          Current Temp Delta - {{current_temp_delta}},
          Action - 
          {% if current_temp_delta < tolerance_delta %}
            Boost Cancelled
          {% else %}
            Boosted By {{[boost_delta_temp, max_boost_delta]|min}}°C for {{boost_time}} mins
          {% endif %}
        entity_id: '{{climate_entity}}'
        domain: wiser
  trigger_variables:
    boost_time: 30
    tolerance_delta: 0.5
    max_boost_delta: 5
  mode: queued
  max: 10
  ```

You should now have a heating system that will use external temp sensors placed anywhere in a room that suits you that will correct the wiser TRV temp sensing and ensure you room it heated to the temperature you expect from your schedule.

If you have rooms that have Wiser in them but no seperate sensor, then that is also fine as it is driven by the sensor updating its reading.  If it's not there, no reading updates!