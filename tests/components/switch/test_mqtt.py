"""
tests.components.switch.test_mqtt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests MQTT switch.
"""
import unittest

from homeassistant.const import STATE_ON, STATE_OFF
import homeassistant.components.switch as switch
from tests.common import (
    mock_mqtt_component, fire_mqtt_message, get_test_home_assistant)


class TestSensorMQTT(unittest.TestCase):
    """ Test the MQTT switch. """

    def setUp(self):  # pylint: disable=invalid-name
        self.hass = get_test_home_assistant()
        self.mock_publish = mock_mqtt_component(self.hass)

    def tearDown(self):  # pylint: disable=invalid-name
        """ Stop down stuff we started. """
        self.hass.stop()

    def test_controlling_state_via_topic(self):
        self.assertTrue(switch.setup(self.hass, {
            'switch': {
                'platform': 'mqtt',
                'name': 'test',
                'state_topic': 'state-topic',
                'command_topic': 'command-topic',
                'payload_on': 'beer on',
                'payload_off': 'beer off'
            }
        }))

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)

        fire_mqtt_message(self.hass, 'state-topic', 'beer on')
        self.hass.pool.block_till_done()

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_ON, state.state)

        fire_mqtt_message(self.hass, 'state-topic', 'beer off')
        self.hass.pool.block_till_done()

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)

    def test_sending_mqtt_commands_and_optimistic(self):
        self.assertTrue(switch.setup(self.hass, {
            'switch': {
                'platform': 'mqtt',
                'name': 'test',
                'command_topic': 'command-topic',
                'payload_on': 'beer on',
                'payload_off': 'beer off',
                'qos': 2
            }
        }))

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)

        switch.turn_on(self.hass, 'switch.test')
        self.hass.pool.block_till_done()

        self.assertEqual(('command-topic', 'beer on', 2, False),
                         self.mock_publish.mock_calls[-1][1])
        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_ON, state.state)

        switch.turn_off(self.hass, 'switch.test')
        self.hass.pool.block_till_done()

        self.assertEqual(('command-topic', 'beer off', 2, False),
                         self.mock_publish.mock_calls[-1][1])
        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)

    def test_controlling_state_via_topic_and_json_message(self):
        self.assertTrue(switch.setup(self.hass, {
            'switch': {
                'platform': 'mqtt',
                'name': 'test',
                'state_topic': 'state-topic',
                'command_topic': 'command-topic',
                'payload_on': 'beer on',
                'payload_off': 'beer off',
                'value_template': '{{ value_json.val }}'
            }
        }))

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)

        fire_mqtt_message(self.hass, 'state-topic', '{"val":"beer on"}')
        self.hass.pool.block_till_done()

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_ON, state.state)

        fire_mqtt_message(self.hass, 'state-topic', '{"val":"beer off"}')
        self.hass.pool.block_till_done()

        state = self.hass.states.get('switch.test')
        self.assertEqual(STATE_OFF, state.state)
