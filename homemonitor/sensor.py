"""Hardware sensors are defined here."""
from abc import ABC, abstractmethod
import logging


class Sensor(ABC):
    """Base class for all sensors.

    :Attributes:
        * name: The name of the alarm.  This will be emailed out.
        * alarm_changed: True if the alarm changed since last call to :meth:`status`.
        * alarm_on: True if the alarm is currently on.
        * hw_error_changed: True if there was a hardware error change since last
            call to :meth:`status`.
        * hw_error_on: True if the hardware is in error state.

    The main loop calls class method :meth:`status`.  If the alarm status
    has changed since the last call, the main loop can send out communication.
    """
    def __init__(self, name):
        """Constructor"""
        self._name = name
        self._alarm_on = False
        self._alarm_on_previous = False
        self._hw_error_on = False
        self._hw_error_on_previous = False
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    @property
    def name(self):
        """Returns the name of the alarm."""
        return self._name

    @property
    def alarm_changed(self):
        """Returns if the alarm changed since the last time :meth:`status` was called."""
        return self.alarm_on != self._alarm_on_previous

    @property
    def alarm_on(self):
        """Returns if the alarm is currently on."""
        return self._alarm_on

    @property
    def hw_error_changed(self):
        """Returns if the hardware error changed."""
        return self.hw_error_on != self._hw_error_on_previous

    @property
    def hw_error_on(self):
        """Returns if the hardware error is currently on."""
        return self._hw_error_on

    def status(self):
        """Updates the status of the sensor.

        If the alarm status has changed, logs a message.
        If the _poll method fails (HW error), logs an error.
        If the error is cleared, logs a message.

        After calling this method, call the properties (attributes) to get the status.
        """
        self._alarm_on_previous = self.alarm_on
        self._hw_error_on_previous = self.hw_error_on
        try:
            self._alarm_on = self._poll()
            self._hw_error_on = False
        except SensorError as error:
            self._hw_error_on = True
            if self.hw_error_changed:
                # Ex: ERROR:homemonitor.sensor:MockSensor - Failed to connect to hardware!
                self.logger.error('%s - %s', self.name, str(error))
            return

        if self.hw_error_changed:
            self.logger.info('%s - OK.', self.name)

        if self.alarm_changed:
            # Ex: INFO:homemonitor.sensor:MockSensor is on.
            self.logger.info('%s is %s.',
                             self.name,
                             self._bool_to_string(self.alarm_on))

    @staticmethod
    def _bool_to_string(value):
        """Converts a boolean to on/off."""
        if value:
            return 'on'
        else:
            return 'off'

    @staticmethod
    def _find_sections_and_names(basename, cfg):
        """Finds all the sections for a given sensor basename.

        :param str basename: Basename of the sensor.
        :param configparser.ConfigParser cfg: Config object.
        :return: List of section, name pairs.
        :rtype: list[list[str, str]]
        """
        section_and_names = []
        for section in cfg.sections():
            if section.startswith(basename):
                _, name = section.split('_')
                section_and_names.append([section, name])

        return section_and_names

    @abstractmethod
    def _poll(self):
        """Polls the sensor.

        :return: True if the alarm is on.  False if the alarm is off.
        :rtype: bool
        :raises SensorError: If something goes wrong with the sensor.

        The class overrides this method to check the actual hardware.
        Only the base class should call this method.
        """
        raise NotImplementedError


class SensorError(Exception):
    """Raised is a hardware error with a sensor."""
    pass


class TemperatureSensor(Sensor):
    """Monitors the temperature in the house."""
    # Config file defines.
    SENSOR_BASE = 'TemperatureSensor'
    TEMPERATURE = 'temperature'

    def __init__(self, name, temperature):
        """Constuctor.

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
        """Contructor.  Read the temperature sensor from a configuration file.

        :param configparser.ConfigParser cfg: The configuration file, in memory.
        :return: List of TemperatureSensor objects.
        :rtype: list[homemonitor.sensor.TemperatureSensor]
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
        return False
