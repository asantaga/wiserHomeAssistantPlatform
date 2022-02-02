# Using External Temp Sensor to Manage Room Temp Accuracy

The basic premise of this automation is to monitor a series of external temperature sensors and boost wiser room heating to reach the correct temperature as set by the schedule.

On updates from the external temp sensor, it will compare this to the scheduled temp of the Wiser climate device (aka room).  If the room is not already heating or boosted, it will boost the room by 1.5x the difference.  I have found this to give pretty good results but this may need tweakign for your own situation.

It will also look if the current room temp is within 0.5C of the scheduled temp and cancel any boost if it is.  Again, this number can be changed but will involve a number of places to change it.

## There are 3 requirements for this automation to work:

1) You need at least version 3.0.20 of the Wiser integration for HA.  It uses the 'current scheduled temp' attribute that was new in this version.
2) That your temperature sensors are setup in HA Areas with the Wiser Climate device you wish to control in the same area, as it looks for a Wiser climate device in the same Area as the temp sensor that triggered a state update to get the scheduled temp and set a boost.
3) The first condition in the automation may/will need to be adjusted to filter your specific temp sensors.  I am using Aqara sensors via the ZHA integration.


Adding new climate devices or temp sensors (providing they are of the same type you already have) should require no changes to this automation.

If you have rooms that have Wiser in them but no seperate sensor, then that is also fine as it is driven by the sensor updating its reading.  If it's not there, no reading updates!

```yaml
alias: Adjust Wiser Boost for Ext Temp Sensor Heat Management
description: Uses External Temp Sensor To Achieve Target Temp in Room
trigger:
  - platform: event
    event_type: state_changed
condition:
  - condition: and
    conditions:
      - condition: template
        value_template: |-
          {% if trigger.event.data.entity_id in integration_entities('zha') and 
              trigger.event.data.entity_id.startswith('sensor.lumi') 
              and trigger.event.data.entity_id.endswith('temperature')
          %}
            True
          {% endif %}
      - condition: template
        value_template: |-
          {% set trigger_entity = trigger.event.data.entity_id %}

          {# find corresponding room climate sensor #}
          {% for wiser_climate in area_entities(area_name(trigger_entity))
              if wiser_climate.startswith('climate.') 
                  and wiser_climate in integration_entities('wiser')
          %}
            {% if loop.first %}
              {% set sensor_temp = states(trigger_entity)|float %}
              {% set schedule_temp = state_attr(wiser_climate, 'current_schedule_temp')|float %}
               {% 
                if (
                    (schedule_temp - sensor_temp) > 0.5 
                    and not state_attr(wiser_climate, 'is_heating')
                    and not state_attr(wiser_climate, 'is_boosted')
                  )
                  or
                  (
                    (schedule_temp - sensor_temp) < 0.5 
                    and state_attr(wiser_climate, 'is_boosted')
                  )
              %}
                True    
              {% endif %}
            {% endif %}
          {% endfor %}
action:
  - service: wiser.boost_heating
    data_template:
      entity_id: >-
        {% set sensor = trigger.event.data.entity_id %} {% for wiser_climate in
        area_entities(area_name(sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser') 
        %}
          {% if loop.first %}{{wiser_climate}}{% endif %}
        {% endfor %}
      time_period: >-
        {% set sensor = trigger.event.data.entity_id %} {% for wiser_climate in
        area_entities(area_name(sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser') 
        %}
          {% if loop.first %}
            {% set sensor_temp = states(sensor)|float %}
            {% set schedule_temp = state_attr(wiser_climate, 'current_schedule_temp')|float %}
            {% set delta = (schedule_temp - sensor_temp)|round(1) %}
            {% if delta < 0.5 %}
              0
            {% else %}
              30
            {% endif %}
          {% endif %}
        {% endfor %}
      temperature_delta: >-
        {% set sensor = trigger.event.data.entity_id %} {% for wiser_climate in
        area_entities(area_name(sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser') 
        %}
          {% if loop.first %}
            {% set sensor_temp = states(sensor)|float %}
            {% set schedule_temp = state_attr(wiser_climate, 'current_schedule_temp')|float %}
            {% set delta = (schedule_temp - sensor_temp)|round(1) %}
            {% if delta < 0.5 %}
              {% set delta = 0 %}
            {% endif %}
            {% set boost_delta = (((delta * 1.5) * 2 )|round(0)/2) %}
            {{boost_delta}}
          {% endif %}
        {% endfor %}
  - service: logbook.log
    data_template:
      name: Wiser Temp Boost by Ext Sensor
      message: |-
        {% set sensor = trigger.event.data.entity_id %}  {% for wiser_climate in
              area_entities(area_name(sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser') 
        %}
          {% if loop.first %}
            {% set sensor_temp = states(sensor)|float %}
            {% set schedule_temp = state_attr(wiser_climate, 'current_schedule_temp')|float %}
            {% set delta = (schedule_temp - sensor_temp)|round(1) %}
            Sensor Temp - {{sensor_temp}}°C, 
            Schedule Temp - {{schedule_temp}}°C, 
            {% if delta < 0.5 %}
              Boost Cancelled
            {% else %}
              {% set boost_delta = (((delta * 1.5) * 2 )|round(0)/2)|round(1) %}
              Boosted By {{boost_delta}}°C
            {% endif %}
          {% endif %}
        {% endfor %}
      entity_id: |-
        {% set sensor = trigger.event.data.entity_id %}  {% for wiser_climate in
              area_entities(area_name(sensor))
              if wiser_climate.startswith('climate.') 
              and wiser_climate in integration_entities('wiser') 
        %}
          {% if loop.first %}
            {{wiser_climate}}
          {% endif %}
        {% endfor %}
      domain: wiser
mode: queued
max: 10
```
