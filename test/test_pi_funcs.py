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
