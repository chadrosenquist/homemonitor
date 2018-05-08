"""Tests the TemperatureSensor class."""

import unittest
from configparser import ConfigParser

from loggingtestcase import capturelogs

from homemonitor.temperaturesensor import TemperatureSensor


class TemperatureSensorFromConfigTestCase(unittest.TestCase):
    """Test's TemperatureSensor."""
    SUCCESS_CONFIG = '''
    [TemperatureSensor_Basement]
    temperature=50

    [TemperatureSensor_Attic]
    temperature=60
    
    [Other_FirstFloor]
    temperature=10
    '''

    @capturelogs()
    def test_success(self, logs):
        """Create two objects from config file."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_CONFIG)
        sensors = TemperatureSensor.from_config(cfg)

        self.assertEqual('TemperatureSensor/Basement', sensors[0].name)
        self.assertEqual(50, sensors[0].temperature)

        self.assertEqual('TemperatureSensor/Attic', sensors[1].name)
        self.assertEqual(60, sensors[1].temperature)

        self.assertEqual(
            ['INFO:homemonitor.sensor:Created sensor TemperatureSensor/Basement with '
             'temperature threshold of 50 degrees.',
             'INFO:homemonitor.sensor:Created sensor TemperatureSensor/Attic with '
             'temperature threshold of 60 degrees.'],
            logs.output)


class TemperatureSensorManualTestcase(unittest.TestCase):
    """Manually run to test the sensor."""
    # pylint: disable=invalid-name
    @classmethod
    @capturelogs('homemonitor', level='DEBUG')
    def Xtest_manual(cls, logs):
        """Manually run to test the sensor.

        sudo pytest -s tests/sensor_test.py::TemperatureSensorManualTestcase::test_manual
        """
        # Use what is in the config file for the sensor.
        cfg = ConfigParser()
        cfg.read('/home/pi/.homemonitor.ini')
        sensor = TemperatureSensor.from_config(cfg)

        # Read the sensor.
        sensor[0].status()

        # Print the logs.
        print('\n')
        print('\n'.join(logs.output))


if __name__ == '__main__':
    unittest.main()
