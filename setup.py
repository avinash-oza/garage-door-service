from setuptools import setup

setup(
        name='garage-door',
        version='0.2b11',
        packages=['garage_door',],
        scripts=['bin/run-garage-door-service', 'bin/nagios_check_garage.py'],
        license='TBD',
        long_description='TBD'
        )
