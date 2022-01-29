# Using External Temp Sensor to Manage Room Temp Accuracy

The basic premise of these scripts is to monitor a series of external temperature sensors and fire an event when their reading changes.

Automation 1 is basically filtering all HA state change events to capture only those from your specific temp sensors.  When it detects one of your sensors has changed temp reading, it raises and event which is the in turn picked up by Automation 2 & 3.

In order for this to work, all you need to do is have your temp sensor and the wiser climate devices in the same HA Area, as it looks for a Wiser climate device in the same Area as the temp sensor.

Adding new climate devices or temp sensors (providing they are of the same type you already have) should require no changes to any of these scripts.

If you have rooms that have Wiser in them but no seperate sensor, then that is also fine as it is driven by the sensor.


# Automation 1

Depending on your sensors you are using, you may need to modify this script.  I am using Aqara sensors connected via ZHA integration.  The value template in the condition is where you will need to modifiy to filter this to your specific sensors.

```
alias: Fire Event when room monitoring temp sensors change reading
description: ''
trigger:
  - platform: event
    event_type: state_changed
condition:
  - condition: template
    value_template: |-
      {{ 
      trigger.event.data.new_state.attributes.device_class == 'temperature'
      and trigger.event.data.entity_id in integration_entities('zha')
      }}
action:
  - event: custom_temp_sensor_changed
    event_data:
      entity_id: '{{trigger.event.data.entity_id}}'
      old_temp: '{{trigger.event.data.old_state.state}}'
      new_temp: '{{trigger.event.data.new_state.state}}'
mode: single

```


# Automation 2
Create an automation with this yaml below.  Apart from maybe changing the 0.5C delta parameter (which is the required difference between the temp sensor reading and the scheduled temp) this is generic to all wiser setups (I think!?)

```
alias: Boost Heating to Meet True Target Temp
description: ''
trigger:
  - platform: event
    event_type: custom_temp_sensor_changed
condition:
  - condition: template
    value_template: |-
      {% set entity_id = trigger.event.data.entity_id %}
      {# Get wiser climate entity in same area #}
      {%- for wiser_entity_id in area_entities(area_name(entity_id))
          if wiser_entity_id.startswith('climate.') 
              and wiser_entity_id in integration_entities('wiser')
      %}
        {% if loop.first %}
          {# If sensor temp reading > schedule set and heating and boosted #}
          {% if states(entity_id)|float - state_attr(wiser_entity_id, 'current_schedule_temp') > 0.5
              and not state_attr(wiser_entity_id, 'is_heating')
              and not state_attr(wiser_entity_id, 'is_boosted')
          %}
            True
          {% endif %}
        {% endif %}
      {% endfor %}
action:
  - service: wiser.boost_heating
    data:
      time_period: 30
      temperature_delta: 2
      entity_id: >
        {% set entity_id = trigger.event.data.entity_id %}  
        {# Get wiser climate entity in same area #}  
        {%- for wiser_entity_id in area_entities(area_name(entity_id))
            if wiser_entity_id.startswith('climate.') 
                and wiser_entity_id in integration_entities('wiser')
        %}
          {% if loop.first %}
               {{ wiser_entity_id }}
          {% endif %}
        {% endfor %}
mode: single

```

# Automation 3
Same as Step 2.  This script is generic and can be used for all Wiser setups.

```
alias: Cancel Boost if Target Room Temp Reached
description: ''
trigger:
  - platform: event
    event_type: custom_temp_sensor_changed
condition:
  - condition: template
    value_template: |-
      {% set entity_id = trigger.event.data.entity_id %}
      {# Get wiser climate entity in same area #}
      {%- for wiser_entity_id in area_entities(area_name(entity_id))
          if wiser_entity_id.startswith('climate.') 
              and wiser_entity_id in integration_entities('wiser')
      %}
        {% if loop.first %}
          {# If sensor temp reading > schedule set and heating and boosted #}
          {% if states(entity_id)|float - state_attr(wiser_entity_id, 'current_schedule_temp') > 0.5
              and state_attr(wiser_entity_id, 'is_heating')
              and state_attr(wiser_entity_id, 'is_boosted')
          %}
            True
          {% endif %}
        {% endif %}
      {% endfor %}
action:
  - service: climate.set_preset_mode
    data:
      entity_id: >
        {% set entity_id = trigger.event.data.entity_id %}  {# Get wiser climate
        entity in same area #}  {%- for wiser_entity_id in
        area_entities(area_name(entity_id))
            if wiser_entity_id.startswith('climate.') 
                and wiser_entity_id in integration_entities('wiser')
        %}
          {% if loop.first %}
               {{ wiser_entity_id }}
          {% endif %}
        {% endfor %}
      preset_mode: Cancel Overrides
mode: single

```
