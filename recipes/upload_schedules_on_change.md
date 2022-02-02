# Automatically Upload Schedule Files on Change

I have 2 sets of schedule files, one for when the house is occupied and one for when not.  More for when we are out for a few hours as opposed to away mode.

I have a folder whater setup in configuration.yaml to monitor file changes in my config/schedules directory.

In this directory are sub folders for occupied and unoccupied.

If I change one of these files, this automation automatically uploads and applies that to the hub.


```yaml
alias: Climate Schedule File Change Upload to Wiser
description: ''
trigger:
  - platform: event
    event_type: folder_watcher
    event_data:
      event_type: modified
condition:
  - condition: template
    value_template: >-
      {{

      (trigger.event.data.file|regex_search('_occupied', ignorecase=TRUE) and
      is_state('sensor.house','Occupied'))

      or

      (trigger.event.data.file|regex_search('_unoccupied', ignorecase=TRUE) and
      is_state('sensor.house','Unoccupied'))

      }}
action:
  - service: persistent_notification.create
    data_template:
      title: Climate Schedule Updated
      message: >
        {%- if is_state('sensor.house','Occupied') -%}
          Updated climate.{{'wiser_' + trigger.event.data.file|regex_replace(find='_schedule_occupied.yaml', replace='', ignorecase=False)}}
        {% else %}
          Updated climate.{{'wiser_' + trigger.event.data.file|regex_replace(find='_schedule_unoccupied.yaml', replace='', ignorecase=False)}}
        {% endif %} from file {{ trigger.event.data.folder }}/{{
        trigger.event.data.file }} 
      notification_id: 8002
  - service: wiser.set_heating_schedule
    data_template:
      entity_id: |
        {%- if is_state('sensor.house','Occupied') -%}
          climate.{{'wiser_' + trigger.event.data.file|regex_replace(find='_schedule_occupied.yaml', replace='', ignorecase=False)}}
        {% else %}
          climate.{{'wiser_' + trigger.event.data.file|regex_replace(find='_schedule_unoccupied.yaml', replace='', ignorecase=False)}}
        {% endif %}
      filename: '{{ trigger.event.data.folder }}/{{ trigger.event.data.file }}'
mode: single
```