"""Tests the main event loop."""
import unittest
from unittest.mock import Mock
from configparser import ConfigParser

from homemonitor.eventloop import EventLoop
from homemonitor.mailqueue import MailQueue, Message

from tests.sensor_test import MockSensor


class EventLoopTestCase(unittest.TestCase):
    """Tests the main event loop."""
    def test_alarm_mail(self):
        """Tests alarm email is sent."""
        mailqueue = Mock(MailQueue, autospec=True)
        mailqueue.add = Mock(return_value=None, autospec=True)
        sensor1 = MockSensor(poll_results=[True, False])
        # noinspection PyTypeChecker
        eventloop = EventLoop(mailqueue,
                              [sensor1],
                              poll_interval_in_seconds=.001,
                              loop_forever=False)

        # Alarm on email sent.
        eventloop.run()
        self.assertEqual(Message('MockSensor is on.', 'MockSensor is on.'),
                         mailqueue.add.call_args_list[0][0][0])
        self.assertEqual(1, mailqueue.send.call_count)

        # Alarm off email is sent.
        eventloop.run()
        self.assertEqual(Message('MockSensor is off.', 'MockSensor is off.'),
                         mailqueue.add.call_args_list[1][0][0])
        self.assertEqual(2, mailqueue.send.call_count)

    def test_hw_failure_mail(self):
        """Tests hardware failure email is sent."""
        mailqueue = Mock(MailQueue, autospec=True)
        mailqueue.add = Mock(return_value=None, autospect=True)
        sensor1 = MockSensor(poll_results=[False, False], error_results=[True, False])
        # noinspection PyTypeChecker
        eventloop = EventLoop(mailqueue,
                              [sensor1],
                              poll_interval_in_seconds=.001,
                              loop_forever=False)

        # HW failure email sent.
        eventloop.run()
        self.assertEqual(Message('MockSensor has detected a hardware failure.',
                                 'MockSensor has detected a hardware failure.'),
                         mailqueue.add.call_args_list[0][0][0])
        self.assertEqual(1, mailqueue.send.call_count)

        # HW OK email sent.
        eventloop.run()
        self.assertEqual(Message('MockSensor hardware is OK.',
                                 'MockSensor hardware is OK.'),
                         mailqueue.add.call_args_list[1][0][0])
        self.assertEqual(2, mailqueue.send.call_count)


class EventLoopFromConfigTest(unittest.TestCase):
    """Tests creating an EventLoop from a config file."""
    SUCCESS_CONFIG = '''
    [eventloop]
    poll_interval_in_seconds=10
    '''

    def test_success(self):
        """Create EventLoop object from configuration file."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_CONFIG)
        mailqueue = Mock()
        sensor = Mock()
        # noinspection PyTypeChecker
        eventloop = EventLoop.from_config(cfg, mailqueue, [sensor])
        self.assertEqual(10, eventloop.poll_interval_in_seconds)

    SUCCESS_DEFAULTS_CONFIG = '''
    [eventloop]
    '''

    def test_success_defaults(self):
        """Create EventLoop objects with defaults."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_DEFAULTS_CONFIG)
        mailqueue = Mock()
        sensor = Mock()
        # noinspection PyTypeChecker
        eventloop = EventLoop.from_config(cfg, mailqueue, [sensor])
        self.assertEqual(EventLoop.DEFAULT_POLL_INTERVAL, eventloop.poll_interval_in_seconds)


if __name__ == '__main__':
    unittest.main()
