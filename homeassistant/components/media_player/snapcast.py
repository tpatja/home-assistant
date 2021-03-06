"""
homeassistant.components.media_player.snapcast
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides functionality to interact with Snapcast clients.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.snapcast/
"""

import logging
import socket

from homeassistant.const import (
    STATE_ON, STATE_OFF)

from homeassistant.components.media_player import (
    MediaPlayerDevice,
    SUPPORT_VOLUME_SET, SUPPORT_VOLUME_MUTE)

SUPPORT_SNAPCAST = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE
DOMAIN = 'snapcast'
REQUIREMENTS = ['snapcast==1.1.1']
_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the Snapcast platform. """
    import snapcast.control
    host = config.get('host')
    port = config.get('port', snapcast.control.CONTROL_PORT)
    if not host:
        _LOGGER.error('No snapserver host specified')
        return
    try:
        server = snapcast.control.Snapserver(host, port)
    except socket.gaierror:
        _LOGGER.error('Could not connect to Snapcast server at %s:%d',
                      host, port)
        return
    add_devices([SnapcastDevice(client) for client in server.clients])


class SnapcastDevice(MediaPlayerDevice):
    """ Represents a Snapcast client device. """

    # pylint: disable=abstract-method

    def __init__(self, client):
        self._client = client

    @property
    def name(self):
        """ Device name. """
        return self._client.identifier

    @property
    def volume_level(self):
        """ Volume level. """
        return self._client.volume / 100

    @property
    def is_volume_muted(self):
        """ Volume muted. """
        return self._client.muted

    @property
    def supported_media_commands(self):
        """ Flags of media commands that are supported. """
        return SUPPORT_SNAPCAST

    @property
    def state(self):
        """ State of the player. """
        if self._client.connected:
            return STATE_ON
        return STATE_OFF

    def mute_volume(self, mute):
        """ Mute status. """
        self._client.muted = mute

    def set_volume_level(self, volume):
        """ Volume level. """
        self._client.volume = round(volume * 100)
