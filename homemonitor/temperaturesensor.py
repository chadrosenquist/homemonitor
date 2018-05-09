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
    GPIO = 'gpio'
    MODEL = 'model'

    MODELS = ('DHT11', 'DHT22', 'AM2302')

    def __init__(self, name, temperature, gpio, model):
        """Constructor.

        :param str name: Name of the sensor.
        :param int temperature: When temperator goes below, set off the alarm.
        :param int gpio: GPIO pin the sensor is connected.
        :param str model: DHT11, DHT22, or AM2302.
        :raises ValueError: If model is invalid.
        """
        super().__init__(name)
        self.temperature = temperature
        self.gpio = gpio

        model = model.upper()
        self._validate_model(name, model)
        self.model = model

        self.logger.info('Created %s', str(self))

    @classmethod
    def _validate_model(cls, name, model):
        """Validates the model is correct."""
        if model not in cls.MODELS:
            raise ValueError('For {}, model {} is not a valid model!  Valid models are: {}'.format(
                name, model, cls.MODELS))

    def __str__(self):
        """Returns string representation of the class.

        :return: String representation of the class.
        :rtype: str
        """
        format_string = 'TemperatureSensor {} with temperature threshold of {} degrees, ' \
                        'connected to GPIO {}, and model {}.'
        return format_string.format(self.name, self.temperature, self.gpio, self.model)

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
            gpio=4
            model=AM2302

            [TemperatureSensor_Attic]
            temperature=60
            gpio=25
            model=dht11

        """
        return_sensors = []

        section_and_names = cls._find_sections_and_names(cls.SENSOR_BASE, cfg)
        for section, name in section_and_names:
            temperature = cfg.getint(section, cls.TEMPERATURE)
            gpio = cfg.getint(section, cls.GPIO)
            model = cfg.get(section, cls.MODEL)
            new_sensor = cls('{}/{}'.format(cls.SENSOR_BASE, name),
                             temperature,
                             gpio,
                             model)
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

        model_to_enum = {'DHT11': Adafruit_DHT.DHT11,
                         'DHT22': Adafruit_DHT.DHT22,
                         'AM2302': Adafruit_DHT.AM2302}

        sensor = model_to_enum[self.model]
        pin = self.gpio
        _, temperature_celcius = Adafruit_DHT.read_retry(sensor, pin)

        if temperature_celcius is None:
            raise SensorError('Failed to read {}!'.format(self.name))

        temperature_fahrenheit = int(temperature_celcius * 9/5.0 + 32)
        self.logger.debug('TemperatureSensor %s is detecting %s degrees Fahrenheit',
                          self.name,
                          temperature_fahrenheit)

        return temperature_fahrenheit < self.temperature
