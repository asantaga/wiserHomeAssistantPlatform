# Home Assistant Recipe's 

This page documents some Home Assistant recipe's collected from the community - Than



## Collection of Sensors ( **[phixion](https://github.com/phixion)**)

Following files assume you are separating out you configuration.yaml file into separate files (e.g. sensor.yaml,binary_sensor.yaml etc) as per https://www.home-assistant.io/docs/configuration/splitting_configuration/. if you want you can put these all in a single `configuration.yaml`.



binary_sensor.yaml: sensor to check if heating is turned on or off, also sets a suiting icon

```yaml
- platform: template
    heating_flur:
      friendly_name: Heating Flur
      value_template: '{{state_attr("climate.wiser_flur","control_output_state") == "On"}}'
      icon_template: >-
        {% if is_state("binary_sensor.heating_flur", "on") %}
          mdi:radiator
        {% else %}
          mdi:radiator-off
        {% endif %}
```

sensor.yaml: history_stat sensor **for today** utilizing the binary sensor from above

```yaml
- platform: history_stats
  name: Heating Flur On Today
  entity_id: binary_sensor.heating_flur
  state: 'on'
  type: time
  start: "{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}"
  end: "{{ now() }}"
```

sensor.yaml: history_stat sensor **for yesterday** utilizing the binary sensor from above

```yaml
- platform: history_stats
  name: Heating Flur On Yesterday
  entity_id: binary_sensor.heating_flur
  state: 'on'
  type: time
  end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
  duration:
    hours: 24
```

sensor.yaml: history_stat sensor **for this week so far** utilizing the binary sensor from above

```yaml
- platform: history_stats
  name: Heating Flur On this Week
  entity_id: binary_sensor.heating_flur
  state: 'on'
  type: time
  start: "{{ as_timestamp( now().replace(hour=0).replace(minute=0).replace(second=0) ) - now().weekday() * 86400 }}"
  end: "{{ now() }}"
```

sensor.yaml: history_stat sensor **for the past 30 days** utilizing the binary sensor from above

```yaml
- platform: history_stats
  name: Heating Flur On past 30 days
  entity_id: binary_sensor.heating_flur
  state: 'on'
  type: time
  end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
  duration:
    days: 30
```

sensor.yaml: history_stats spits out unitof measuerment in hours, so here is a simple conversion

```yaml
- platform: template
  sensors:
    heating_time_flur:
      friendly_name: Heating Time Flur
      icon_template: mdi:radiator
      value_template: "{{ states('sensor.heating_flur_on_today') | float * 60 }}"
      unit_of_measurement: min
```



## Custom Lovelace Card (https://gist.github.com/phixion)



![](docs/phixion-card-graphic.png)



```yaml
# Template sensors to strip battery values out of their attributes
# Defaults to value 101, comes hin handy when crafting lovelace cards
# sets device class to battery to take care of fancy automated templated battery icons
# sets correct unit

    thermostat_wohnzimmer_battery_level:
      friendly_name: Thermostat Wohnzimmer Batterie
      value_template: "{{ states.sensor.wiser_itrv_wohnzimmer.attributes.battery_percent | default(101) | int if states.sensor.wiser_itrv_wohnzimmer.attributes.battery_percent is not none}}"
      device_class: battery
      unit_of_measurement: "%"
    thermostat_bad_battery_level:
      friendly_name: Thermostat Bad Batterie
      value_template: "{{ states.sensor.wiser_itrv_bad.attributes.battery_percent | default(101) | int if states.sensor.wiser_itrv_bad.attributes.battery_percent is not none}}"
      device_class: battery
      unit_of_measurement: "%"
    thermostat_flur_battery_level:
      friendly_name: Thermostat Flur Batterie
      value_template: "{{ states.sensor.wiser_itrv_flur.attributes.battery_percent | default(101) | int if states.sensor.wiser_itrv_flur.attributes.battery_percent is not none}}"
      device_class: battery
      unit_of_measurement: "%"
    thermostat_roomstat_battery_level:
      friendly_name: Raum Thermostat Batterie
      value_template: "{{ states.sensor.wiser_roomstat_wohnzimmer.attributes.battery_percent | default(101) | int if states.sensor.wiser_roomstat_wohnzimmer.attributes.battery_percent is not none}}"
      device_class: battery
      unit_of_measurement: "%"
      
# Lovelace card to create Battery Level bars out of our values with the help of auto-entities and custom bar card
# to draw a bar the battery value must be <101 otherwise its discarded, without ugly ui error messages 
# can look like https://i.phx.ms/P7Bi.png and https://i.phx.ms/vvwL.png
# card can easily be adapted to other battery attributes
card:
  align: split
  columns: 1
  height: 20
  rounding: 0px
  severity:
    - color: '#ff165d'
      value: 30
    - color: '#ff9a00'
      value: 60
    - color: '#3ec1d3'
      value: 100
  title_position: inside
  title_style:
    font-size: 14px
  type: 'custom:bar-card'
  unit_of_measurement: '%'
  value_style:
    font-size: 14px
  width: 100%
filter:
  include:
    - entity_id: sensor.thermostat*battery_level
      state: <101
type: 'custom:auto-entities'
```







