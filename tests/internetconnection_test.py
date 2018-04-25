import unittest
import socket
from unittest.mock import patch
from loggingtestcase import capturelogs
from configparser import ConfigParser

from homemonitor.internetconnection import CheckInternetConnection


class InternetConnectionTest(unittest.TestCase):
    @classmethod
    def Xtest_internet_manual(cls):
        check_internet_connection = CheckInternetConnection(port=100, timeout_in_seconds=1)
        print('\n\nInternet connection? {}'.format(check_internet_connection.connected()))

    @capturelogs('homemonitor')
    @patch.object(socket.socket, 'connect', return_value=None)
    def test_internet_up(self, logs, socket_patch):
        self.assertTrue(CheckInternetConnection().connected())
        socket_patch.assert_called_once()
        self.assertEqual(logs.output, [], 'There are no logs because the Internet is up.')

    @capturelogs('homemonitor')
    @patch.object(socket.socket, 'connect', side_effect=TimeoutError)
    def test_internet_down(self, logs, socket_patch):
        connection = CheckInternetConnection()
        self.assertFalse(connection.connected())
        socket_patch.assert_called_once()
        self.assertRegex(logs.output[0],
                         'No Internet connection.  Check your Internet connection and '
                         'verify {0}:{1} is correct.'.format(connection.server, connection.port))

    @capturelogs('homemonitor')
    def test_down_and_up(self, logs):
        """The Internet went down and then came back up.

        The Internet is down for the first three checks and
        is then back up for the next two checks.
        """
        with patch.object(socket.socket, 'connect', MockSocket().connect):
            connection = CheckInternetConnection()
            self.assertFalse(connection.connected())
            self.assertFalse(connection.connected())
            self.assertFalse(connection.connected())
            self.assertTrue(connection.connected())
            self.assertTrue(connection.connected())
            self.assertRegex(logs.output[0],
                             'No Internet connection.')
            self.assertRegex(logs.output[1],
                             'Internet connection restored.')


class MockSocket(object):
    """Mocks a connection between down.

    The first down_count (3) times connect() is invoked, raises an
    exception, simulating the Internet being down.
    After that, returns without error, simulating the Internet being back up again.
    """
    def __init__(self, down_count=3):
        self.connect_call_count = 0
        self.down_count = down_count

    # noinspection PyUnusedLocal,PyUnusedLocal
    def connect(self, *args, **kwargs):
        self.connect_call_count += 1
        if self.connect_call_count <= self.down_count:
            raise TimeoutError('test')


class InternetConnectionFromConfigTest(unittest.TestCase):
    SUCCESS_CONFIG = '''
    [internet]
    server=ping.com
    port=100
    timeout_in_seconds=30
    '''

    def test_success(self):
        """Create from config file."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_CONFIG)
        connection = CheckInternetConnection.from_config(cfg)
        self.assertEquals(connection.server, 'ping.com')
        self.assertEquals(connection.port, 100)
        self.assertEquals(connection.timeout_in_seconds, 30)

    SUCCESS_DEFAULT_CONFIG = '''
    [internet]
    '''

    def test_success_default(self):
        """Create from config file, using defaults."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_DEFAULT_CONFIG)
        connection = CheckInternetConnection.from_config(cfg)
        self.assertEquals(connection.server, CheckInternetConnection.DEFAULT_SERVER)
        self.assertEquals(connection.port, CheckInternetConnection.DEFAULT_PORT)
        self.assertEquals(connection.timeout_in_seconds,
                          CheckInternetConnection.DEFAULT_TIMEOUT_IN_SECONDS)


if __name__ == '__main__':
    unittest.main()
