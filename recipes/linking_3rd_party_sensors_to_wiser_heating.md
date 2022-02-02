# Linking 3rd Party TRVs/Sensors to Wiser Heating

------

@carloneb had the following scenario

He has a Drayton Wiser Basic Kit one thermostat in the kitchen but he doesnt have a Wiser TRV in the main room, he does however have a SONOFF Zibbee temperature sensor which is already integrated with Home Assistant. Can he get the heating to trigger the request for heat when the main room is cold? without purchasing a new TRV?

YES YES YES!

## How

Definitions:

In `Configuration.yaml`, defined a new generic thermostat entity for the kitchen: “cucina”. This thermostat is commanding a switch (defined later) which is then triggering the Wiser’s commands. Also, the generic thermostat is linked to the Sonoff Temperature sensor (sensor.t_cucina_temperature).

```yaml
climate:
  - platform: generic_thermostat
    name: cucina
    heater: switch.switch_t_cucina
    target_sensor: sensor.t_cucina_temperature
    min_temp: 5
    max_temp: 30
    ac_mode: false
    target_temp: 20
    cold_tolerance: 0.3
    hot_tolerance: 0
    initial_hvac_mode: "heat"
# Linking 3rd Party TRVs/Sensors to Wiser Heating

------

@carloneb had the following scenario

He has a Drayton Wiser Basic Kit one thermostat in the kitchen but he doesnt have a Wiser TRV in the main room, he does however have a SONOFF Zibbee temperature sensor which is already integrated with Home Assistant. Can he get the heating to trigger the request for heat when the main room is cold? without purchasing a new TRV?

YES YES YES!

## How

Definitions:

In `Configuration.yaml`, defined a new generic thermostat entity for the kitchen: “cucina”. This thermostat is commanding a switch (defined later) which is then triggering the Wiser’s commands. Also, the generic thermostat is linked to the Sonoff Temperature sensor (sensor.t_cucina_temperature).

```yaml
climate:
  - platform: generic_thermostat
    name: cucina
    heater: switch.switch_t_cucina
    target_sensor: sensor.t_cucina_temperature
    min_temp: 5
    max_temp: 30
    ac_mode: false
    target_temp: 20
    cold_tolerance: 0.3
    hot_tolerance: 0
    initial_hvac_mode: "heat"

```

The switch used by the above thermostat is as follows. It calls the wiser.boost_heating service when on (demanding heat) and sets the wiser to auto when triggered off (target T reached).

```yaml
switch:
  - platform: template
    switches:
      switch_t_cucina:
        turn_on:
      service: wiser.boost_heating
        data:
        entity_id: climate.wiser_soggiorno
        time_period: 30
        temperature: 21
        temperature_delta: 1
        turn_off:
      service: climate.set_hvac_mode
        data:
        entity_id: climate.wiser_soggiorno
    hvac_mode: "auto"
```

Because the main temperature scheduling is owned by the wiser (it’s the master), I’ve created an automation that “copy” the scheduled temperature from the wiser to the Sonoff thermostat at any change.

```yaml
- alias: Set target T cucina
  description: Setta la T target di climate.cucina quando la T schedulata wiser cambia, tranne se in boost
  condition:
    condition: numeric_state
    entity_id: climate.wiser_soggiorno
      attribute: boost_remaining
    below: 1
  trigger:
  - platform: state
    entity_id: sensor.target_t
    action:
  - service: climate.set_temperature
    data:
    entity_id: climate.cucina
    temperature: "{{ (states('sensor.target_t') | float) }}"
```

In this way I can have both rooms heat following the scheduling set in the Wiser.

![sensors](D:\My\Src\Home\HA Stuff\wiserHomeAssistantPlatform\docs\nonwisersensor_image.jpg)


```

The switch used by the above thermostat is as follows. It calls the wiser.boost_heating service when on (demanding heat) and sets the wiser to auto when triggered off (target T reached).

```yaml
switch:
  - platform: template
    switches:
      switch_t_cucina:
        turn_on:
      service: wiser.boost_heating
        data:
        entity_id: climate.wiser_soggiorno
        time_period: 30
        temperature: 21
        temperature_delta: 1
        turn_off:
      service: climate.set_hvac_mode
        data:
        entity_id: climate.wiser_soggiorno
    hvac_mode: "auto"
```

Because the main temperature scheduling is owned by the wiser (it’s the master), I’ve created an automation that “copy” the scheduled temperature from the wiser to the Sonoff thermostat at any change.

```yaml
- alias: Set target T cucina
  description: Setta la T target di climate.cucina quando la T schedulata wiser cambia, tranne se in boost
  condition:
    condition: numeric_state
    entity_id: climate.wiser_soggiorno
      attribute: boost_remaining
    below: 1
  trigger:
  - platform: state
    entity_id: sensor.target_t
    action:
  - service: climate.set_temperature
    data:
    entity_id: climate.cucina
    temperature: "{{ (states('sensor.target_t') | float) }}"
```

In this way I can have both rooms heat following the scheduling set in the Wiser.

![sensors](D:\My\Src\Home\HA Stuff\wiserHomeAssistantPlatform\docs\nonwisersensor_image.jpg)

