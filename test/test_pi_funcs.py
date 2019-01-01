import sys
from unittest import TestCase, mock

# override the RPi import
sys.modules['RPi'] = mock.Mock()

from garage_door.pi_funcs import get_garage_status, trigger_garage


@mock.patch('garage_door.pi_funcs.GPIO')
class PiFuncsTestCase(TestCase):
    def setUp(self):
        # mock LEFT garage as closed and right as open
        self.garage_sensor_status = lambda pin: {25: 0, 16: 1}[pin]
        self.garage_sensor_trigger = lambda pin: {27: 0, 22: 1}[pin]

        self.gpio_HIGH = mock.Mock('HIGH')
        self.gpio_LOW = mock.Mock('LOW')

    def test_check_right_garage_open(self, mock_gpio):
        mock_gpio.input.side_effect = self.garage_sensor_status

        self.assertEqual(get_garage_status('RIGHT'), 1)

    def test_check_left_garage_closed(self, mock_gpio):
        mock_gpio.input.side_effect = self.garage_sensor_status

        self.assertEqual(get_garage_status('LEFT'), 0)

    def test_invalid_garage(self, mock_gpio):
        mock_gpio.input.side_effect = self.garage_sensor_status

        with self.assertRaises(ValueError):
            get_garage_status('ABC')
        self.assertFalse(mock_gpio.input.called)

    def test_invalid_value(self, mock_gpio):
        mock_gpio.input.side_effect = lambda pin: {25: 0.5 }[pin]

        with self.assertRaises(ValueError):
            get_garage_status('LEFT')
        mock_gpio.input.assert_called_with(25)

    def test_trigger_garage(self, mock_gpio):
        mock_gpio.HIGH = self.gpio_HIGH
        mock_gpio.LOW = self.gpio_LOW

        trigger_garage('LEFT')

        self.assertEqual(2, mock_gpio.output.call_count)

        mock_gpio.output.assert_has_calls([mock.call(27, self.gpio_HIGH),
                                           mock.call(27, self.gpio_LOW)])
