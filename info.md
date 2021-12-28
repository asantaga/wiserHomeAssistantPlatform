{% if prerelease %}
### Please note: This is a Beta version and may have some instabilities.
{% endif %}

{% if installed and version_installed.replace("v", "").0 | int < 3  %}
  ## v3 Upgrade Warning
  This upgrade contains a high number of breaking changes from v2.x.  Please read the [Updating to v3.0](https://github.com/asantaga/wiserHomeAssistantPlatform/tree/v3#updating-to-v30---important-please-read) documentation before proceeding.

{% endif %}

This integration allows visibility and control of the Drayton Wiser system in Home Assistant. For information about how to configure and the features included in the integration, please see the [Readme.md](https://github.com/asantaga/wiserHomeAssistantPlatform/blob/v3/Readme.Md)


