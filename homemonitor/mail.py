import smtplib
import logging


class Mail(object):
    """Send email.

    Example::

        from homemonitor.mail import Mail, MailException

        try:
            the_mail = Mail('sender@gmail.com', 'password', ['receiver@gmail.com'])
            the_mail.send('hi', 'Hi from Mail class.')
        except MailException as error:
            print('Error: {}'.format(error))

    """

    def __init__(self, user, password, to, server='smtp.gmail.com', port=587):
        """Constructor.

        :param str user: User name of the account used to send email.
        :param str password: Password of the account.
        :param list to: List of users to send emails.
        :param str server: SMTP server to connect.
        :param int port: Port of the SMTP server.
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
