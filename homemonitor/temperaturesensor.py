"""Temperature sensors are defined in this module.

Supports the following sensors from Adafruit_DHT:
    * DHT11
    * DHT22
    * AM2302

"""

from homemonitor.sensor import Sensor, SensorError


class TemperatureSensor(Sensor):
    """Monitors the temperature in the house."""
    # Config file defines.
    SENSOR_BASE = 'TemperatureSensor'
    TEMPERATURE = 'temperature'

    def __init__(self, name, temperature):
        """Constructor.

        :param str name: Name of the sensor.
        :param int temperature: When temperator goes below, set off the alarm.
        """
        super().__init__(name)
        self.temperature = temperature

        self.logger.info('Created sensor %s with temperature threshold of %s degrees.',
                         self.name,
                         self.temperature)

    @classmethod
    def from_config(cls, cfg):
        """Constructor.  Read the temperature sensor from a configuration file.

        :param configparser.ConfigParser cfg: The configuration file, in memory.
        :return: List of TemperatureSensor objects.
        :rtype: list[homemonitor.temperaturesensor.TemperatureSensor]
        :raises configparser.Error: If any options are missing or other options files issues.

        Note: Currently only one sensor is supported.  In the future, maybe have multiple
        sensors and this function will return a list of sensors?

        Example::

            [TemperatureSensor_Basement]
            temperature=50

            [TemperatureSensor_Attic]
            temperature=60

        """
        return_sensors = []

        section_and_names = cls._find_sections_and_names(cls.SENSOR_BASE, cfg)
        for section, name in section_and_names:
            temperature = cfg.getint(section, cls.TEMPERATURE)
            new_sensor = cls('{}/{}'.format(cls.SENSOR_BASE, name),
                             temperature)
            return_sensors.append(new_sensor)

        return return_sensors

    def _poll(self):
        """Polls the sensor.

        :return: True if the alarm is on.  False if the alarm is off.
        :rtype: bool
        :raises SensorError: If something goes wrong with the sensor.
        """
        # noinspection PyUnresolvedReferences
        # pylint: disable=import-error
        import Adafruit_DHT

        sensor = Adafruit_DHT.AM2302
        pin = 4
        _, temperature_celcius = Adafruit_DHT.read_retry(sensor, pin)

        if temperature_celcius is None:
            raise SensorError('Failed to read {}!'.format(self.name))

        temperature_fahrenheit = int(temperature_celcius * 9/5.0 + 32)
        self.logger.debug('TemperatureSensor = %s degrees Fahrenheit', temperature_fahrenheit)

        return temperature_fahrenheit < self.temperature
