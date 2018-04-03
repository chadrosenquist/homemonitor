from abc import ABC, abstractmethod
import smtplib
import socket
import logging


class Mail(ABC):
    """Send email

    Example::

        from homemonitor.mail import GMail, MailException

        try:
            the_mail = GMail('hello@gmail.com', 'password')
            the_mail.send('hi', 'Hi from GMail class.')
        except MailException as error:
            print('Error: {}'.format(error))

    """
    @abstractmethod
    def send(self, subject, body):
        """Sends email.

        :param str subject: subject
        :param str body: body
        :raises MailException: If failed to send email.
        """
        pass


class MailException(Exception):
    pass


class GMail(Mail):
    def __init__(self, user, password, server='smtp.gmail.com', port=587):
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())

    def send(self, subject, body):
        """Sends email.

        :param str subject: subject
        :param str body: body
        :raises MailException: If failed to send email.
        """
        message = self._message(body, subject)
        smtp = self._connect()
        self._login_and_send(message, smtp)
        self._logger.info('Sent email to {0} with subject "{1}".'.format(self.user, subject))

    def _message(self, body, subject):
        headers = [
            'From: ' + self.user,
            'Subject: ' + subject,
            'To: ' + self.user,
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
        except socket.gaierror as error:
            message = 'Failed to send email.  Verify {0}:{1} is correct. {2}'.format(self.server,
                                                                                     self.port,
                                                                                     str(error))
            self._logger.error(message)
            raise MailException(message) from error
        return smtp

    def _login_and_send(self, message, smtp):
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, self.user, message)
        except smtplib.SMTPAuthenticationError as error:
            message = 'Failed to send email.  Check user/password is correct - {}'.format(str(error))
            self._logger.error(message)
            raise MailException(message) from error
        finally:
            smtp.quit()
