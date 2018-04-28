"""Main event loop."""
import time

from homemonitor.mailqueue import Message


class EventLoop(object):
    """Main event loop."""
    DEFAULT_POLL_INTERVAL = 900  # 15 minutes

    # Config file defines.
    SECTION = 'eventloop'
    POLL_INTERVAL = 'poll_interval_in_seconds'

    """Main event loop."""
    def __init__(self,
                 mailqueue,
                 sensors,
                 poll_interval_in_seconds=DEFAULT_POLL_INTERVAL,
                 loop_forever=True):
        """Constructor.

        :param homemonitor.mailqueue.MailQueue mailqueue: Used to send email.
        :param list[homemonitor.sensor.Sensor] sensors: List of sensors to check.
        :param int poll_interval_in_seconds: Seconds to sleep between polling sensors.
        :param bool loop_forever: If True, loop forever.  If False, only loop once
            (used for unit testing.)
        """
        self.mailqueue = mailqueue
        self.sensors = sensors
        self.poll_interval_in_seconds = poll_interval_in_seconds
        self.loop_forever = loop_forever

    @classmethod
    def from_config(cls, cfg, mailqueue, sensors):
        """Constructor.  Creates a EventLoop object from a config file.

        :param configparser.ConfigParser cfg: The configuration file, in memory.
        :param homemonitor.mailqueue.MailQueue mailqueue: Used to send email.
        :param list[homemonitor.sensor.Sensor] sensors: List of sensors to check.
        :return: EventLoop object.
        :rtype: homemonitor.eventloop.EventLoop
        :raises configparser.Error: If any options are missing or other options files issues.

        Example::

            [eventloop]
            poll_interval_in_seconds=900

        """
        poll_interval = cfg.getint(cls.SECTION,
                                   cls.POLL_INTERVAL,
                                   fallback=cls.DEFAULT_POLL_INTERVAL)
        return cls(mailqueue, sensors, poll_interval)

    @staticmethod
    def _bool_to_string(value):
        """Converts a boolean to on/off.

        Note: Function is duplicated in Sensor class!
        """
        if value:
            return 'on'
        else:
            return 'off'

    def _hw_failure_email(self, sensor):
        if sensor.hw_error_changed:
            if sensor.hw_error_on:
                content = '{} has detected a hardware failure.'.format(sensor.name)
            else:
                content = '{} hardware is OK.'.format(sensor.name)
            self.mailqueue.add(Message(content, content))

    def _alarm_email(self, sensor):
        if sensor.alarm_changed:
            content = '{} is {}.'.format(sensor.name,
                                         self._bool_to_string(sensor.alarm_on))
            self.mailqueue.add(Message(content, content))

    def run(self):
        """Runs the main loop of the program.

        * Sleep
        * Refresh status of all the sensors.
        * If the status changed, add email to the queue.
        * Allow the queue a chance to send email.
        """
        while True:
            time.sleep(self.poll_interval_in_seconds)
            for sensor in self.sensors:
                sensor.status()
                # Note: This code is similar to the Sensor logging.  Should it be in Sensor instead?
                self._alarm_email(sensor)
                self._hw_failure_email(sensor)

            self.mailqueue.send()

            if not self.loop_forever:
                break
