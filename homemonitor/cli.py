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


DEFAULT_CONFIG_FILE = os.path.join('$HOME', '.homemonitor.ini')


def _print_version():
    print('{}'.format(homemonitor.version.__version__))


def _print_help():
    print('python homemonitor [option]')
    print('    -h|--help: Print help.')


def _send_test_mail(mailqueue):
    """Sends a test email.

    :param homemonitor.mailqueue.MailQueue mailqueue: Queue used to send out test email.
    """
    message = Message('Test email from homemonitor.',
                      'Hi,\r\n\r\n'
                      'This is a test email from the homemonitor on your Raspbery Pi.  '
                      'Hopefully you received this email just fine and your config file is setup correctly.\r\n\r\n'
                      'Sincerely,\r\n'
                      'HomeMonitor')
    mailqueue.add(message)
    print('Sending test email to {}...'.format(mailqueue.mail.to))
    mailqueue.send()
    print('Done.  Check your inbox.')


def main(argv):
    test_mode = False
    config_file = DEFAULT_CONFIG_FILE

    # Handle options.
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

    # Create objects.
    try:
        mail = Mail.from_config(cfg)
        check_internet_connection = CheckInternetConnection.from_config(cfg)
    except configparser.Error as error:
        print('\nError: Failed to read config file "{0}" : {1}\n'.format(config_file, str(error)),
              file=sys.stderr)
        return 1
    mailqueue = MailQueue(mail, check_internet_connection)

    # Set up logging.
    logging.config.fileConfig(config_file)

    # Send test email.
    if test_mode:
        _send_test_mail(mailqueue)
        return 0

    # Main event loop.
    # ???

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
