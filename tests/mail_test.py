import unittest
from unittest.mock import patch
import smtplib

from homemonitor.mail import GMail, MailException
from loggingtestcase import capturelogs


class GMailTest(unittest.TestCase):
    @classmethod
    def Xtest_manual(cls):
        """Manually test.

        Enter your gmail username and the application passwcode.
        Run this test and check your gmail account for the email.
        """
        the_mail = GMail('user@gmail.com', 'application passcode')
        the_mail.send('mail_test.py', 'Hello, I am from mail_test.py!')

    @capturelogs('homemonitor', 'INFO')
    def test_invalid_server(self, logs):
        """smtp.connect() fails.

        Also verify smtp.quit() doesn't get called (it throws an exception).
        * Verify MailException correctly raised.
        * Verify error is written to the logs.
        """
        the_mail = GMail('test@gmail.com', 'password', server='thisisabadservername.com')
        with self.assertRaisesRegex(MailException, 'thisisabadservername'):
            the_mail.send('hi', 'Hello!')
        self.assertRegex(logs.output[0], 'Failed to send email.')

    def test_server_timeout(self):
        """smtp.connect() times out."""
        the_mail = GMail('test@gmail.com', 'pasword')
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
        the_mail = GMail('test@gmail.com', 'pasword')
        with self.assertRaisesRegex(MailException,
                                    'Failed to send email.  Check user\(test@gmail.com\)/password is correct'):
            with patch.object(smtplib.SMTP,
                              'login',
                              return_value=None,
                              side_effect=smtplib.SMTPAuthenticationError(2, 'test')):
                the_mail.send('hi', 'Hello!')
        self.assertRegex(logs.output[0], 'Failed to send email.  Check user\(test@gmail.com\)/password is correct')

    @capturelogs('homemonitor', 'INFO')
    def test_success(self, logs):
        """Successfully calls the mock with the correct message."""
        the_mail = GMail('test@gmail.com', 'pasword')
        with patch.object(smtplib.SMTP, 'login', return_value=None, autospec=True):
            with patch.object(smtplib.SMTP, 'sendmail', return_value=None, autospec=True) as mock_sendmail:
                the_mail.send('hi', 'Hello!')
                self.assertEqual(mock_sendmail.call_args[0][1], 'test@gmail.com')
                self.assertEqual(mock_sendmail.call_args[0][2], 'test@gmail.com')
                self.assertMultiLineEqual(str(mock_sendmail.call_args[0][3]),
                                          'From: test@gmail.com\r\n'
                                          'Subject: hi\r\n'
                                          'To: test@gmail.com\r\n'
                                          'MIME-Version: 1.0\r\n'
                                          'Content-Type: text/html'
                                          '\r\n'
                                          '\r\n'
                                          'Hello!')
            self.assertEqual(logs.output,
                             ['INFO:homemonitor.mail:Sent email to test@gmail.com with subject "hi".'])


if __name__ == '__main__':
    unittest.main()
