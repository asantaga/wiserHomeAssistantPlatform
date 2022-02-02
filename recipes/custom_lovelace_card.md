## Custom Lovelace Card (https://gist.github.com/phixion)

------



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