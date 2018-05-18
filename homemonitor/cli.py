"""Command Line Interface (cli)"""
import sys
import getopt
import os
from configparser import ConfigParser
import configparser
import logging
import logging.config

import homemonitor.version
from homemonitor.mail import Mail
from homemonitor.internetconnection import CheckInternetConnection
from homemonitor.mailqueue import MailQueue, Message
from homemonitor.eventloop import EventLoop
from homemonitor.temperaturesensor import TemperatureSensor

DEFAULT_CONFIG_FILE = os.path.join(os.sep, 'home', 'pi', 'homemonitor', '.homemonitor.ini')


def _print_version():
    print('{}'.format(homemonitor.version.__version__))


def _print_help():
    print('python homemonitor [option]')
    print('    -h|--help: Print help.')
    print('    -v|--version: Version')
    print('    -t|--test: Send a test email and test all sensors.')
    print('    -c=|--config=: Give location of configuration file.')
    print('        Defaults to {}'.format(DEFAULT_CONFIG_FILE))


def _send_test_mail(mailqueue):
    """Sends a test email.

    :param homemonitor.mailqueue.MailQueue mailqueue: Queue used to send out test email.
    """
    message = Message('Test email from homemonitor.',
                      'Hi,\r\n\r\n'
                      'This is a test email from the homemonitor on your Raspbery Pi.  '
                      'Hopefully you received this email just fine and'
                      ' your config file is setup correctly.\r\n\r\n'
                      'Sincerely,\r\n'
                      'HomeMonitor')
    mailqueue.add(message)
    print('Sending test email to {}...'.format(mailqueue.mail.receivers))
    mailqueue.send()
    print('Done.  Check your inbox.')


def _test_sensors(sensors):
    """Tests out each sensor.

    :param list[homemonitor.sensor.Sensor] sensors: List of sensors to check.
    """
    # The sensor print out additional logging when DEBUG is on.
    level = logging.DEBUG
    logger = logging.getLogger('homemonitor')
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

    for sensor in sensors:
        sensor.status()


def main(argv):
    """Main Event Loop

    * Handle command line options.
    * Read config file.
    * Set up logging.
    * Create objects from config file.
    * Test mode.
    * Loop forever.
    """
    test_mode = False
    config_file = DEFAULT_CONFIG_FILE

    # Handle command line options.
    options, _ = getopt.getopt(argv, 'vhtc:', ['version', 'help', 'test', 'config='])
    for option, opt_value in options:
        if option in ('-v', '--version'):
            _print_version()
            return 0
        elif option in ('-h', '--help'):
            _print_help()
            return 1
        elif option in ('-t', '--test'):
            test_mode = True
        elif option in ('-c', '--config'):
            config_file = opt_value

    # Read in config file.
    config_file = os.path.expandvars(config_file)
    cfg = ConfigParser()
    with open(config_file, 'r') as file:
        cfg.read_file(file)

    # Set up logging.
    logging.config.fileConfig(config_file)

    # Create objects.
    try:
        mail = Mail.from_config(cfg)
        check_internet_connection = CheckInternetConnection.from_config(cfg)
        mailqueue = MailQueue(mail, check_internet_connection)
        sensors = list()
        sensors.extend(TemperatureSensor.from_config(cfg))
        eventloop = EventLoop.from_config(cfg, mailqueue, sensors)
    except configparser.Error as error:
        print('\nError: Failed to read config file "{0}" : {1}\n'.format(config_file, str(error)),
              file=sys.stderr)
        return 1

    # Test.
    if test_mode:
        _send_test_mail(mailqueue)
        _test_sensors(sensors)
        return 0

    # Main event loop.
    eventloop.run()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
