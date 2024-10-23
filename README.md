# OctoPrint PSU Control - RestAPI
Adds Rest API support to OctoPrint-PSUControl as a sub-plugin  
(Forked form Erik de Keijzer's OctoPrint-PSUControl-HomeAssistant)

## Setup
- Install the plugin using Plugin Manager from Settings
- Configure this plugin
- Select this plugin as Switching *and* Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)
- :warning: **Turn off** the *Automatically turn PSU ON* option in the PSU Control settings, leaving this on will ruin your prints when Home Assistant becomes unavailable :warning: (some explanation in tickets
[#4](https://github.com/edekeijzer/OctoPrint-PSUControl-HomeAssistant/issues/4), 
[#11](https://github.com/edekeijzer/OctoPrint-PSUControl-HomeAssistant/issues/11), 
[#16](https://github.com/edekeijzer/OctoPrint-PSUControl-HomeAssistant/issues/16))

## Configuration
* Enter the Host URL of your Rest API server
* Enter the API key


## Support
Please check your logs first. If they do not explain your issue, open an issue in GitHub. Please set *octoprint.plugins.psucontrol* and *octoprint.plugins.psucontrol_restapi* to **DEBUG** and include the relevant logs. Feature requests are welcome as well.

## Todo
- [x] Add descriptions to settings page
- [ ] Add images to documentation
