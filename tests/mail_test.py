"""Tests Mail class."""
import unittest
from unittest.mock import patch
import smtplib
from configparser import ConfigParser

from loggingtestcase import capturelogs

from homemonitor.mail import Mail, MailException


class MailTest(unittest.TestCase):
    """Tests Mail class."""
    # pylint: disable=invalid-name
    @classmethod
    def Xtest_manual(cls):
        """Manually test.

        Enter your gmail username and the application passwcode.
        Run this test and check your gmail account for the email.
        """
        the_mail = Mail('sender@gmail.com', 'password', receivers=['receiver@gmail.com'])
        the_mail.send('mail_test.py', 'Hello, I am from mail_test.py!')

    # noinspection PyTypeChecker
    def test_receivers_is_not_list(self):
        """Tests the receivers parameter not being a list throws an exception."""
        with self.assertRaises(ValueError):
            Mail('sender@mail.com', 'password', receivers='receiver@mail.com')

    @capturelogs('homemonitor', 'INFO')
    def test_invalid_server(self, logs):
        """smtp.connect() fails.

        Also verify smtp.quit() doesn't get called (it throws an exception).
        * Verify MailException correctly raised.
        * Verify error is written to the logs.
        """
        the_mail = Mail('test@mail.com',
                        'password',
                        ['receiver@mail.com'],
                        server='thisisabadservername.com')
        with self.assertRaisesRegex(MailException, 'thisisabadservername'):
            the_mail.send('hi', 'Hello!')
        self.assertRegex(logs.output[0], 'Failed to send email.')

    def test_server_timeout(self):
        """smtp.connect() times out."""
        the_mail = Mail('test@mail.com', 'pasword', ['receiver@mail.com'])
        with self.assertRaises(MailException):
            with patch.object(smtplib.SMTP,
                              'connect',
                              return_value=None,
                              side_effect=TimeoutError('timed out')):
                the_mail.send('hi', 'Hello!')

    @capturelogs('homemonitor', 'INFO')
    def test_invalid_user(self, logs):
        """smtp.login() fails.

        Use a mock so we don't have failed login attempts against the real Google server.
        """
        the_mail = Mail('test@mail.com', 'pasword', ['receiver@mail.com'])
        with self.assertRaisesRegex(MailException,
                                    r'Failed to send email.  '
                                    r'Check user\(test@mail.com\)/password is correct'):
            with patch.object(smtplib.SMTP,
                              'login',
                              return_value=None,
                              side_effect=smtplib.SMTPAuthenticationError(2, 'test')):
                the_mail.send('hi', 'Hello!')
        self.assertRegex(logs.output[0],
                         r'Failed to send email.  Check user\(test@mail.com\)/password is correct')

    @capturelogs('homemonitor', 'INFO')
    def test_success(self, logs):
        """Successfully calls the mock with the correct message."""
        the_mail = Mail('test@mail.com', 'pasword', ['receiver1@mail.com', ' receiver2@mail.com '])
        with patch.object(smtplib.SMTP,
                          'login',
                          return_value=None,
                          autospec=True):
            with patch.object(smtplib.SMTP,
                              'sendmail',
                              return_value=None,
                              autospec=True) as mock_sendmail:
                the_mail.send('hi', 'Hello!')
                self.assertEqual(mock_sendmail.call_args[0][1], 'test@mail.com')
                self.assertEqual(mock_sendmail.call_args[0][2], 'test@mail.com')
                self.assertMultiLineEqual(str(mock_sendmail.call_args[0][3]),
                                          'From: test@mail.com\r\n'
                                          'Subject: hi\r\n'
                                          'To: receiver1@mail.com,receiver2@mail.com\r\n'
                                          'MIME-Version: 1.0\r\n'
                                          'Content-Type: text/plain'
                                          '\r\n'
                                          '\r\n'
                                          'Hello!')
            self.assertEqual(['INFO:homemonitor.mail:Sent email to [\'receiver1@mail.com\', '
                              '\' receiver2@mail.com \'] with subject "hi".'],
                             logs.output)


class MailFromConfigTest(unittest.TestCase):
    """Tests creating Mail object from a config file."""
    SUCCESS_CONFIG = '''
    [mail]
    user=test@mail.com
    password=password123
    receivers=receiver1@mail.com, receiver2@mail.com
    server=mailserver.com
    port=123
    '''

    def test_success(self):
        """Create Mail object from configuration file."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_CONFIG)
        mail = Mail.from_config(cfg)
        self.assertEqual(mail.user, 'test@mail.com')
        self.assertEqual(mail.password, 'password123')
        self.assertEqual(mail.receivers, ['receiver1@mail.com', 'receiver2@mail.com'])
        self.assertEqual(mail.server, 'mailserver.com')
        self.assertEqual(mail.port, 123)

    SUCCESS_DEFAULTS_CONFIG = '''
    [mail]
    user=test@mail.com
    password=password123
    receivers=receiver1@mail.com, receiver2@mail.com
    '''

    def test_success_defaults(self):
        """Create Mail objects with defaults."""
        cfg = ConfigParser()
        cfg.read_string(self.SUCCESS_DEFAULTS_CONFIG)
        mail = Mail.from_config(cfg)
        self.assertEqual(mail.server, Mail.DEFAULT_SERVER)
        self.assertEqual(mail.port, Mail.DEFAULT_PORT)


if __name__ == '__main__':
    unittest.main()
