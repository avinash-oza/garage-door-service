import sys
from unittest import TestCase, mock

# mock out gpio
from .mock_RPi import RPi
sys.modules['RPi'] = RPi

from garage_door.pi_funcs import get_garage_status


class PiFuncsTestCase(TestCase):
    def test_import(self):
        get_garage_status('LEFT')