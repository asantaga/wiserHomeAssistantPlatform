# Renaming History Graphs Element Names 

------

If you want to rename element names in the history graphs you can. There are two ways you can do this. 

## Method 1

Add an override of the to the entity in the Lovelace UI (i.e. the name: Upstairs bit below).

```yaml
entities:
  - entity: climate.wiser_upstairs
    name: Upstairs
hours_to_show: 12
refresh_interval: 0
title: Upstairs Heating
type: history-graph
So now they read "Upstairs current temperature", "Upstairs heating" and "Upstairs target temperature". Still a little long, so I tried a space character and that works although the "c" in "current " is in lowercase :-(

entities:
  - entity: climate.wiser_upstairs
    name: ' '
hours_to_show: 12
refresh_interval: 0
title: Upstairs Heating
type: history-graph
```

## Method 2

Create template sensors from the attributes of the climate sensor. 

e.g.
```yaml
sensor:
  - platform: template
    sensors:
      lounge_current_temp:
        friendly_name: "Current"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('climate.wiser_lounge','current_temperature')}}"
        
      lounge_target_temp:
        friendly_name: "Target"
        unit_of_measurement: "°C"
        value_template: "{{ state_attr('climate.wiser_lounge','temperature')}}"
        
      lounge_heating:
        friendly_name: "Heating"
        value_template: "{{ state_attr('climate.wiser_lounge','control_output_state')}}"
```
if these are added to the  history graphs, elements will be named as per the friendly names above.