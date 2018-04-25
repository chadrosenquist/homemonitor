"""Checks for an internet connection."""
import socket
import logging


class CheckInternetConnection(object):
    """Checks if there is an Internet connection by opening a socket."""

    # Config file defines.
    SECTION = 'internet'
    SERVER = 'server'
    PORT = 'port'
    TIMEOUT_IN_SECONDS = 'timeout_in_seconds'
    DEFAULT_SERVER = 'google.com'
    DEFAULT_PORT = 80
    DEFAULT_TIMEOUT_IN_SECONDS = 20

    def __init__(self,
                 server=DEFAULT_SERVER,
                 port=DEFAULT_PORT,
                 timeout_in_seconds=DEFAULT_TIMEOUT_IN_SECONDS):
        """Constructor.  Checks for Internet connection.

        :param str server: Host to connect.  Defaults to :attr:`DEFAULT_SERVER`.
        :param int port: Port to connect.  Defaults to :attr:`DEFAULT_PORT`.
        :param int timeout_in_seconds: Timeout in seconds.
            Defaults to :attr:`DEFAULT_TIMEOUT_IN_SECONDS`.
        """
        self.server = server
        self.port = port
        self.timeout_in_seconds = timeout_in_seconds
        self._internet_up = True
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    @classmethod
    def from_config(cls, cfg):
        """Constructor.  Create object from config file.

        :param configparser.ConfigParser cfg: The configuration file, in memory.
        :return: CheckInternetConnection object.
        :rtype: homemonitor.internetconnection.CheckInternetConnection
        :raises configparser.Error: If any options are missing or other options files issues.

        Example::

            [internet]
            server=ping.com
            port=100
            timeout_in_seconds=30

        """
        server = cfg.get(cls.SECTION, cls.SERVER, fallback=cls.DEFAULT_SERVER)
        port = cfg.getint(cls.SECTION, cls.PORT, fallback=cls.DEFAULT_PORT)
        timeout_in_seconds = cfg.getint(cls.SECTION,
                                        cls.TIMEOUT_IN_SECONDS,
                                        fallback=cls.DEFAULT_TIMEOUT_IN_SECONDS)
        return cls(server, port, timeout_in_seconds)

    def connected(self):
        """Performs the actual check for Internet connection.

        :return: True if connection, false if currently no connection.
        :rtype: bool

        * If connection goes form up to down, log an ERROR message.
        * If connection goes from down to up, log an INFO message.
        """
        new_internet_up = self._ping_host()
        if self._internet_up and not new_internet_up:
            # The Internet was up and now it is down.
            self.logger.error('No Internet connection.  Check your Internet connection and '
                              'verify %s:%s is correct.',
                              self.server,
                              self.port)
        elif not self._internet_up and new_internet_up:
            # Internet was down and is now up.
            self.logger.info('Internet connection restored.')

        self._internet_up = new_internet_up

        return new_internet_up

    def _ping_host(self):
        with socket.socket() as ping_socket:
            try:
                ping_socket.settimeout(self.timeout_in_seconds)
                ping_socket.connect((self.server, self.port))
                return True
            except OSError:
                return False
