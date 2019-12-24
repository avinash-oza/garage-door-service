import time

from RPi import GPIO

# Pi specific constants relative to looking at the house
RELAY_PIN_MAPPING = {'LEFT' : 27, 'RIGHT': 17}
GARAGE_SENSOR_MAPPING = {'LEFT': 25, 'RIGHT': 16}
SORTED_KEYS = [k for k in sorted(RELAY_PIN_MAPPING)] # Sort keys so order is the same

class GarageStatus:
    CLOSED = 0
    OPEN = 1

    def __init__(self, name, pin_value):
        """
        :param name: Garage name
        :param pin_value: the raw value
        """
        # TODO: check if this is needed
        if pin_value not in (self.OPEN, self.CLOSED):
            raise ValueError("Pin value of {} is invalid".format(pin_value))

        self._name = name
        self._pin_value = pin_value

    @property
    def is_open(self):
        """
        True if the garage is open, else False
        :return: bool
        """
        return bool(self._pin_value)

    @property
    def name(self):
        return self._name.capitalize()

    def __repr__(self):
        return "OPEN" if self.is_open else "CLOSED"

def setup_pins():
    GPIO.setmode(GPIO.BCM)
    for one_pin in RELAY_PIN_MAPPING.values():
        GPIO.setup(one_pin, GPIO.OUT)

    for one_pin in GARAGE_SENSOR_MAPPING.values():
        GPIO.setup(one_pin, GPIO.IN)


def cleanup_pins():
    GPIO.cleanup()


def trigger_garage(garage_name):
    relay_pin = RELAY_PIN_MAPPING[garage_name]
    GPIO.output(relay_pin, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(relay_pin, GPIO.LOW)


def get_garage_status(garage_name):
    """
    Gets the garage status specified. Throws an exception if an invalid name is passed
    :param garage_name:
    :return: GarageStatus
    """
    if garage_name not in GARAGE_SENSOR_MAPPING:
        raise ValueError("Invalid garage name passed")

    pin_result = GPIO.input(GARAGE_SENSOR_MAPPING[garage_name])
    return GarageStatus(garage_name, bool(pin_result))