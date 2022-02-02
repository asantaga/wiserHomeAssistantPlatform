# Turn Off Away Mode At Date & Time
By @msp1974

I wrote this quick automation when we went away over New Year to turn off away mode when we were due to come back as I always forget in the joy that is the journey home from holiday!

Create a datetime helper, put this on a card in your Lovelace UI and use this to set the date/time you want to cancel away mode so that when you get home, the house is nice and warm.  Change the trigger at value to be the name of your datetime input.

```yaml
alias: Turn off Away Mode
description: ''
trigger:
  - platform: time
    at: input_datetime.return_home
condition: []
action:
  - service: switch.turn_off
    target:
      entity_id: switch.wiser_away_mode
mode: single
```