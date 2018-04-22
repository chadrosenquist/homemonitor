from abc import ABC, abstractmethod
import logging


class Sensor(ABC):
    """Base class for all sensors.

    :Attributes:
        * alarm_changed: True if the alarm changed since last call to :meth:`status`.
        * alarm_on: True if the alarm is currently on.
        * hw_error_changed: True if there was a hardware error change since last call to :meth:`status`.
        * hw_error_on: True if the hardware is in error state.

    The main loop calls class method :meth:`status`.  If the alarm status
    has changed since the last call, the main loop can send out communication.
    """
    def __init__(self):
        self._alarm_on = False
        self._alarm_on_previous = False
        self._hw_error_on = False
        self._hw_error_on_previous = False
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    @property
    def alarm_changed(self):
        return self.alarm_on != self._alarm_on_previous

    @property
    def alarm_on(self):
        return self._alarm_on

    @property
    def hw_error_changed(self):
        return self.hw_error_on != self._hw_error_on_previous

    @property
    def hw_error_on(self):
        return self._hw_error_on

    def status(self):
        """Updates the status of the sensor.

        If the alarm status has changed, logs a message.
        If the _poll method fails (HW error), logs an error.  If the error is cleared, logs a message.

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
                self.logger.error('{} - {}'.format(self.__class__.__name__, str(error)))
            return

        if self.hw_error_changed:
            self.logger.info('{} - OK.'.format(self.__class__.__name__))

        if self.alarm_changed:
            # Ex: INFO:homemonitor.sensor:MockSensor is on.
            self.logger.info('{} is {}.'.format(self.__class__.__name__,
                                                self._bool_to_string(self.alarm_on)))

    @staticmethod
    def _bool_to_string(value):
        """Converts a boolean to on/off."""
        if value:
            return 'on'
        else:
            return 'off'

    @abstractmethod
    def _poll(self):
        """Polls the sensor.

        :raises SensorError: If something goes wrong with the sensor.

        The class overrides this method to check the actual hardware.
        Only the base class should call this method.
        """
        raise NotImplementedError


class SensorError(Exception):
    pass
