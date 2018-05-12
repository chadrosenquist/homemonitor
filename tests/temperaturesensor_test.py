"""Tests the TemperatureSensor class."""

import unittest
from unittest.mock import patch, MagicMock
from configparser import ConfigParser

from loggingtestcase import capturelogs

from homemonitor.temperaturesensor import TemperatureSensor


class TemperatureSensorFromConfigTestCase(unittest.TestCase):
    """Test's TemperatureSensor."""
    SUCCESS_CONFIG = '''
    [TemperatureSensor_Basement]
    temperature=50
    gpio=4
    model=AM2302

    [TemperatureSensor_SecondFloor]
    temperature=60
    gpio=25
    model=dht11
    
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
        self.assertEqual(4, sensors[0].gpio)
        self.assertEqual('AM2302', sensors[0].model)

        self.assertEqual('TemperatureSensor/SecondFloor', sensors[1].name)
        self.assertEqual(60, sensors[1].temperature)
        self.assertEqual(25, sensors[1].gpio)
        self.assertEqual('DHT11', sensors[1].model)

        self.assertEqual(
            'INFO:homemonitor.sensor:Created TemperatureSensor TemperatureSensor/Basement '
            'with temperature threshold of 50 degrees, connected to GPIO 4, and model '
            'AM2302.',
            logs.output[0])
        self.assertEqual(
            'INFO:homemonitor.sensor:Created TemperatureSensor TemperatureSensor/SecondFloor '
            'with temperature threshold of 60 degrees, connected to GPIO 25, and model '
            'DHT11.',
            logs.output[1])

    FAILURE_CONFIG = '''
    [TemperatureSensor_Basement]
    temperature=50
    gpio=4
    model=VM11111
    '''

    def test_model_invalid(self):
        """Model is invalid."""
        cfg = ConfigParser()
        cfg.read_string(self.FAILURE_CONFIG)
        with self.assertRaisesRegex(ValueError,
                                    r"For TemperatureSensor/Basement, model VM11111 is not a "
                                    r"valid model!  Valid models are: "
                                    r"\('DHT11', 'DHT22', 'AM2302'\)"):
            TemperatureSensor.from_config(cfg)


class TemperatureSensorWithPatchTestcase(unittest.TestCase):
    """Tests patching calls to Adafruit_DHT module."""
    @capturelogs('homemonitor.sensor', 'DEBUG')
    def test_alarm_off(self, logs):
        """Alarm is off."""
        # Module Adafruit_DHT is only installed on Raspberry Pi, so mock it!
        adafruit_patch = MagicMock()
        adafruit_patch.read_retry = MagicMock(return_value=(0, 16))
        adafruit_patch.DHT22 = 'MockDTH22'
        with patch.dict("sys.modules", Adafruit_DHT=adafruit_patch):
            sensor = TemperatureSensor('TEST', 55, 4, 'DHT22')
            sensor.status()

            # Verify alarm and hw error are correct.
            self.assertFalse(sensor.alarm_on,
                             'The alarm should not be on.')
            self.assertFalse(sensor.hw_error_on,
                             'The hardware error alarm should not be on.')

            # Verify read_retry() was called with correct arguments.
            self.assertEqual('MockDTH22',
                             adafruit_patch.read_retry.call_args_list[0][0][0],
                             'adafruit_patch.read_retry() should be called with sensor type '
                             'MockDTH22.')
            self.assertEqual(4,
                             adafruit_patch.read_retry.call_args_list[0][0][1],
                             'adafruit_patch.read_retry() should be called with gpio pin 4.')

            # Verify logging is correct.
            self.assertEqual('DEBUG:homemonitor.sensor:TemperatureSensor TEST is detecting 60 '
                             'degrees Fahrenheit',
                             logs.output[1])

    def test_alarm_on(self):
        """Alarm is on."""
        adafruit_patch = MagicMock()
        adafruit_patch.read_retry = MagicMock(return_value=(0, 10))
        with patch.dict("sys.modules", Adafruit_DHT=adafruit_patch):
            sensor = TemperatureSensor('TEST', 55, 4, 'DHT22')
            sensor.status()
            self.assertTrue(sensor.alarm_on,
                            'The alarm should be on.')

    def test_hw_error_on(self):
        """Hardware error is on."""
        adafruit_patch = MagicMock()
        adafruit_patch.read_retry = MagicMock(return_value=(None, None))
        with patch.dict("sys.modules", Adafruit_DHT=adafruit_patch):
            sensor = TemperatureSensor('TEST', 55, 4, 'DHT22')
            sensor.status()
            self.assertTrue(sensor.hw_error_on,
                            'The hardware error should be on.')


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
