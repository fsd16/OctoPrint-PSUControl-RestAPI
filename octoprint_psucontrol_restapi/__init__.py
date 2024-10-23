# coding=utf-8
from __future__ import absolute_import

__author__ = "Finn Drabsch <finndrabsch@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = (
    "Copyright (C) 2021 Erik de Keijzer - Released under terms of the AGPLv3 License"
)

import octoprint.plugin
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class PSUControl_HomeAssistant(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.RestartNeedingPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
):

    def __init__(self):
        self.config = dict()

    def get_settings_defaults(self):
        return dict(
            address="",
            api_key="",
            on_endpoint="",
            off_endpoint="",
            state_endpoint="",
            verify_certificate=True,
        )

    def on_settings_initialized(self):
        self.reload_settings()

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or "register_plugin" not in psucontrol_helpers.keys():
            self._logger.warning(
                "The version of PSUControl that is installed does not support plugin registration."
            )
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers["register_plugin"](self)

    def send(self, cmd, data=None):
        url = self.config["address"] + cmd

        headers = dict(Authorization="Bearer " + self.config["api_key"])

        response = None
        verify_certificate = self.config["verify_certificate"]
        try:
            self._logger.debug("Starting request to: " + url)
            if data:
                response = requests.post(
                    url, headers=headers, data=data, verify=verify_certificate
                )
            else:
                response = requests.get(url, headers=headers, verify=verify_certificate)
        except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
            self._logger.error("Unable to communicate with server. Check settings.")
        except Exception:
            self._logger.exception("Exception while making API call")
        else:
            if data:
                self._logger.debug(
                    "cmd={}, data={}, status_code={}, text={}".format(
                        cmd, data, response.status_code, response.text
                    )
                )
            else:
                self._logger.debug(
                    "cmd={}, status_code={}, text={}".format(
                        cmd, response.status_code, response.text
                    )
                )

            if response.status_code == 401:
                self._logger.warning("Server returned 401 Unauthorized. Check API key.")
                response = None
            elif response.status_code == 404:
                self._logger.warning("Server returned 404 Not Found. Check Entity ID.")
                response = None

        return response

    def change_psu_state(self, state):

        cmd = "/" + self.config[state + "_endpoint"].lstrip("/")

        self.send(cmd)

    def turn_psu_on(self):
        self._logger.debug("Switching PSU On")
        self.change_psu_state("on")

    def turn_psu_off(self):
        self._logger.debug("Switching PSU Off")
        self.change_psu_state("off")

    def get_psu_state(self):
        self._logger.debug("Getting PSU state")
        cmd = "/" + self.config["state_endpoint"]

        response = self.send(cmd)
        if not response:
            return False
        data = response.json()

        status = None
        try:
            status = data["value"]
        except KeyError:
            pass

        if status == None:
            self._logger.error("Unable to determine status. Check settings.")
            status = False

        return status

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    def get_update_information(self):
        return dict(
            psucontrol_homeassistant=dict(
                displayName="PSU Control - Rest API",
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                user="fsd16",
                repo="OctoPrint-PSUControl-RestAPI",
                current=self._plugin_version,
                # update method: pip w/ dependency links
                pip="https://github.com/fsd16/OctoPrint-PSUControl-RestAPI/archive/{target_version}.zip",
            )
        )


__plugin_name__ = "PSU Control - Rest API"
__plugin_pythoncompat__ = ">=3,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_HomeAssistant()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
