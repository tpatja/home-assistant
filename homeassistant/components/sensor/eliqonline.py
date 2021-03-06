"""
homeassistant.components.sensor.eliqonline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Monitors home energy use for the eliq online service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.eliqonline/
"""
import logging
from urllib.error import URLError
from homeassistant.helpers.entity import Entity
from homeassistant.const import (STATE_UNKNOWN, CONF_ACCESS_TOKEN, CONF_NAME)

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['eliqonline==1.0.11']
DEFAULT_NAME = "ELIQ Energy Usage"


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the Eliq sensor. """

    import eliqonline

    access_token = config.get(CONF_ACCESS_TOKEN)
    name = config.get(CONF_NAME, DEFAULT_NAME)
    channel_id = config.get("channel_id")

    if access_token is None:
        _LOGGER.error(
            "Configuration Error: "
            "Please make sure you have configured your access token "
            "that can be aquired from https://my.eliq.se/user/settings/api")
        return False

    api = eliqonline.API(access_token)
    add_devices([EliqSensor(api, channel_id, name)])


class EliqSensor(Entity):
    """ Implements a Eliq sensor. """

    def __init__(self, api, channel_id, name):
        self._name = name
        self._unit_of_measurement = "W"
        self._state = STATE_UNKNOWN

        self.api = api
        self.channel_id = channel_id
        self.update()

    @property
    def name(self):
        """ Returns the name. """
        return self._name

    @property
    def icon(self):
        """ Returns icon. """
        return "mdi:speedometer"

    @property
    def unit_of_measurement(self):
        """ Unit of measurement of this entity, if any. """
        return self._unit_of_measurement

    @property
    def state(self):
        """ Returns the state of the device. """
        return self._state

    def update(self):
        """ Gets the latest data. """
        try:
            response = self.api.get_data_now(channelid=self.channel_id)
            self._state = int(response.power)
        except (TypeError, URLError):
            _LOGGER.error("could not connect to the eliqonline servers")
