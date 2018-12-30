import time

from garage_door.mock_gpio import GPIO
# import RPi.GPIO as GPIO

# Pi specific constants relative to looking at the house
RELAY_PIN_MAPPING = {'LEFT' : 27, 'RIGHT': 22}
GARAGE_SENSOR_MAPPING = {'LEFT': 25, 'RIGHT': 16}
SORTED_KEYS = [k for k in sorted(RELAY_PIN_MAPPING)] # Sort keys so order is the same

# 0 is CLOSED
# 1 is OPEN
#TODO: Make this an enum
CLOSE = CLOSED = 0
OPEN = 1


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
    # GPIO.output(relay_pin,GPIO.HIGH)
    time.sleep(0.5)
    # GPIO.output(relay_pin,GPIO.LOW)


def get_garage_status(garage_name):
    """
    Gets the garage status specified. Throws an exception if an invalid name is passed
    :param garage_name:
    :return:
    """
    if garage_name not in GARAGE_SENSOR_MAPPING:
        raise ValueError("Invalid garage name passed")

    pin_result = GPIO.input(GARAGE_SENSOR_MAPPING[garage_name])
    if pin_result in (OPEN, CLOSED):
        return bool(pin_result)

    raise ValueError("Pin value of {} is invalid".format(pin_result))

def value_to_status(value):
    """
    returns the position given a number
    :param value:
    :return:
    """
    return 'CLOSED' if value == 0 else 'OPEN'