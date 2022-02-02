## Collection of Sensors ( **[phixion](https://github.com/phixion)**)

------

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