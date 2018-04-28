import unittest
from loggingtestcase import capturelogs

from homemonitor.sensor import Sensor, SensorError


class SensorTestCase(unittest.TestCase):
    """Tests the alarm going on and back on again."""

    @capturelogs('homemonitor.sensor', 'INFO')
    def test_on_then_off(self, logs):
        sensor = MockSensor(poll_results=[False, True, True, False, False])

        # The alarm is off.
        sensor.status()
        self.assertEqual(False, sensor.alarm_changed)
        self.assertEqual(False, sensor.alarm_on)
        self.assertEqual(0, len(logs.output),
                         'There should not be logs if the alarm did not change.')

        # The alarm went on.
        sensor.status()
        self.assertEqual(True, sensor.alarm_changed)
        self.assertEqual(True, sensor.alarm_on)
        self.assertEqual('INFO:homemonitor.sensor:MockSensor is on.',
                         logs.output[0])

        # The alarm is still on.
        sensor.status()
        self.assertEqual(False, sensor.alarm_changed)
        self.assertEqual(True, sensor.alarm_on)
        self.assertEqual(1, len(logs.output),
                         'There should not be logs if the alarm did not change.')

        # The alarm went off.
        sensor.status()
        self.assertEqual(True, sensor.alarm_changed)
        self.assertEqual(False, sensor.alarm_on)
        self.assertEqual('INFO:homemonitor.sensor:MockSensor is off.',
                         logs.output[1])

        # The alarm is still off.
        sensor.status()
        self.assertEqual(False, sensor.alarm_changed)
        self.assertEqual(False, sensor.alarm_on)
        self.assertEqual(2, len(logs.output),
                         'There should not be logs if the alarm did not change.')

    @capturelogs('homemonitor.sensor', 'INFO')
    def test_sensor_error(self, logs):
        """Tests the sensor raising an error."""
        sensor = MockSensor(poll_results=[False, False, False, False, False],
                            error_results=[False, True, True, False, False])

        # The hardware is OK.
        sensor.status()
        self.assertEqual(False, sensor.hw_error_changed)
        self.assertEqual(False, sensor.hw_error_on)
        self.assertEqual(0, len(logs.output),
                         'There should not be logs if the hardware status did not change.')

        # The hardware is having an error.
        sensor.status()
        self.assertEqual(True, sensor.hw_error_changed)
        self.assertEqual(True, sensor.hw_error_on)
        self.assertEqual('ERROR:homemonitor.sensor:MockSensor - Failed to connect to hardware!',
                         logs.output[0])

        # The hardware is still having an error.
        sensor.status()
        self.assertEqual(False, sensor.hw_error_changed)
        self.assertEqual(True, sensor.hw_error_on)
        self.assertEqual(1, len(logs.output),
                         'There should not be logs if the hardware status did not change.')

        # The hardware OK now.
        sensor.status()
        self.assertEqual(True, sensor.hw_error_changed)
        self.assertEqual(False, sensor.hw_error_on)
        self.assertEqual('INFO:homemonitor.sensor:MockSensor - OK.',
                         logs.output[1])

        # The hardware is still OK.
        sensor.status()
        self.assertEqual(False, sensor.hw_error_changed)
        self.assertEqual(False, sensor.hw_error_on)
        self.assertEqual(2, len(logs.output),
                         'There should not be logs if the hardware status did not change.')

    @capturelogs('homemonitor.sensor', 'INFO')
    def test_alarm_and_hw_change(self, logs):
        """Tests hardware and alarm changes at once."""
        sensor = MockSensor(poll_results=[False, True], error_results=[True, False])

        # The HW went down.
        sensor.status()
        self.assertEqual(False, sensor.alarm_changed)
        self.assertEqual(False, sensor.alarm_on)
        self.assertEqual(True, sensor.hw_error_changed)
        self.assertEqual(True, sensor.hw_error_on)

        # HW back up and there is an alarm.
        sensor.status()
        self.assertEqual(True, sensor.alarm_changed)
        self.assertEqual(True, sensor.alarm_on)
        self.assertEqual(True, sensor.hw_error_changed)
        self.assertEqual(False, sensor.hw_error_on)

        self.assertEqual(['ERROR:homemonitor.sensor:MockSensor - Failed to connect to hardware!',
                          'INFO:homemonitor.sensor:MockSensor - OK.',
                          'INFO:homemonitor.sensor:MockSensor is on.'],
                         logs.output)


class MockSensor(Sensor):
    """Mocks a sensor by returning a list of pre-programmed results."""
    def __init__(self, poll_results=None, error_results=None):
        """Constructor

        :param list(bool) poll_results: List of results method poll() will return.
        :param list(bool) error_results: List of whether or not to throw an error.
        """
        super().__init__('MockSensor')
        self.poll_results = poll_results
        self.poll_results_index = 0
        self.error_results = error_results

    def _poll(self):
        self.poll_results_index += 1

        if self.error_results and self.error_results[self.poll_results_index - 1]:
            raise SensorError('Failed to connect to hardware!')

        result = self.poll_results[self.poll_results_index - 1]
        return result


if __name__ == '__main__':
    unittest.main()
