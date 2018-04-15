import smtplib
import logging


class Mail(object):
    # Config file defines.
    SECTION = 'mail'
    USER = 'user'
    PASSWORD = 'password'
    TO = 'to'
    SERVER = 'server'
    PORT = 'port'
    DEFAULT_SERVER = 'smtp.gmail.com'
    DEFAULT_PORT = 587

    """Send email.

    Example::

        from homemonitor.mail import Mail, MailException

        try:
            the_mail = Mail('sender@gmail.com', 'password', ['receiver@gmail.com'])
            the_mail.send('hi', 'Hi from Mail class.')
        except MailException as error:
            print('Error: {}'.format(error))

    """

    def __init__(self, user, password, to, server=DEFAULT_SERVER, port=DEFAULT_PORT):
        """Constructor.

        :param str user: User name of the account used to send email.
        :param str password: Password of the account.
        :param list to: List of users to send emails.
        :param str server: SMTP server to connect.  Defaults to :attr:`DEFAULT_SERVER`.
        :param int port: Port of the SMTP server.  Defaults to :attr:`DEFAULT_PORT`.
        :raises ValueError: If "to" is not a list.  If a string is passed in, the join in send()
            doesn't work correctly.
        """

        self.user = user
        self.password = password
        self.to = to
        self.server = server
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        if not isinstance(to, list):
            raise ValueError('Parameter "to" must be a list.')

    @classmethod
    def from_config(cls, cfg):
        """Constructor.  Creates a Mail object from a config file.

        :param configparser.ConfigParser cfg: The configuration file, in memory.
        :return: Mail object.
        :rtype: homemonitor.mail.Mail
        :raises configparser.Error: If any options are missing or other options files issues.

        Example::

            [mail]
            user=test@mail.com
            password=password123
            to=receiver1@mail.com, receiver2@mail.com
            server=mailserver.com
            port=123

        """
        user = cfg.get(cls.SECTION, cls.USER)
        password = cfg.get(cls.SECTION, cls.PASSWORD)
        to_string = cfg.get(cls.SECTION, cls.TO)
        to = [current.strip() for current in to_string.split(',')]
        server = cfg.get(cls.SECTION, cls.SERVER, fallback=cls.DEFAULT_SERVER)
        port = cfg.getint(cls.SECTION, cls.PORT, fallback=cls.DEFAULT_PORT)
        return cls(user, password, to, server, port)

    def send(self, subject, body):
        """Sends email.

        :param str subject: subject
        :param str body: body
        :raises MailException: If failed to send email.
        """
        message = self._message(body, subject)
        smtp = self._connect()
        self._login_and_send(message, smtp)
        self.logger.info('Sent email to {0} with subject "{1}".'.format(self.user, subject))

    def _message(self, body, subject):
        headers = [
            'From: ' + self.user,
            'Subject: ' + subject,
            'To: ' + ','.join([current.strip() for current in self.to]),
            'MIME-Version: 1.0',
            'Content-Type: text/html'
        ]
        headers_string = '\r\n'.join(headers)
        message = headers_string + '\r\n\r\n' + body
        return message

    def _connect(self):
        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.server, self.port)
        except OSError as error:
            message = 'Failed to send email.  Verify {0}:{1} is correct. {2}'.format(self.server,
                                                                                     self.port,
                                                                                     str(error))
            self.logger.error(message)
            raise MailException(message) from error
        return smtp

    def _login_and_send(self, message, smtp):
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, self.user, message)
        except smtplib.SMTPAuthenticationError as error:
            message = 'Failed to send email.  Check user({0})/password is correct - {1}'.format(self.user, str(error))
            self.logger.error(message)
            raise MailException(message) from error
        finally:
            smtp.quit()


class MailException(Exception):
    pass
