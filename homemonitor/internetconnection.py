import socket
import logging


class CheckInternetConnection(object):
    """Checks if there is an Internet connection by opening a socket to Google (or another address)."""
    def __init__(self, server='google.com', port=80, timeout_in_seconds=20):
        """Checks for Internet connection.

        :param str server: Host to connect.
        :param int port: Port to connect.
        :param int timeout_in_seconds: Timeout in seconds.
        """
        self.server = server
        self.port = port
        self.timeout_in_seconds = timeout_in_seconds
        self._internet_up = True
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

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
                              'verify {0}:{1} is correct.'.format(self.server, self.port))
        elif not self._internet_up and new_internet_up:
            # Internet was down and is now up.
            self.logger.info('Internet connection restored.')

        self._internet_up = new_internet_up

        return new_internet_up

    def _ping_host(self):
        with socket.socket() as s:
            try:
                s.settimeout(self.timeout_in_seconds)
                s.connect((self.server, self.port))
                return True
            except OSError:
                return False
