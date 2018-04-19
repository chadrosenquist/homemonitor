import unittest
from unittest.mock import Mock
from loggingtestcase import capturelogs

from homemonitor.mail import Mail, MailException
from homemonitor.mailqueue import MailQueue, Message
from homemonitor.internetconnection import CheckInternetConnection


class MailQueueTest(unittest.TestCase):
    def test_second_two_messags(self):
        """Tests sending two messages, with a mock.

        The send method should be called twice, once for each message.
        """
        mail = Mock(Mail)
        check_internet_connection = CheckInternetConnectionMock()
        # noinspection PyTypeChecker
        mailqueue = MailQueue(mail, check_internet_connection)
        mailqueue.add(Message('One', 'BodyOne'))
        mailqueue.add(Message('Two', 'BodyTwo'))
        mailqueue.send()

        # Verify Main.send() was called twice with the correct arguments.
        self.assertEqual(mail.send.call_count, 2)
        self.assertEqual(mail.send.call_args_list[0][0], ('One', 'BodyOne'))
        self.assertEqual(mail.send.call_args_list[1][0], ('Two', 'BodyTwo'))

        # Send a second time.  The call count should remain at 2 because
        # the queue is cleared and Mail.send() is not called again.
        mailqueue.send()
        self.assertEqual(mail.send.call_count, 2)

    @capturelogs('homemonitor')
    def test_fail_three_times(self, logs):
        """Tests failing to send the message three times."""
        mail = Mock(Mail)
        mail.send.side_effect = MailException
        check_internet_connection = CheckInternetConnectionMock()
        # noinspection PyTypeChecker
        mailqueue = MailQueue(mail, check_internet_connection, retries=3)
        mailqueue.add(Message('One', 'BodyOne'))
        for count in range(0, 5):
            mailqueue.send()
        self.assertEqual(mail.send.call_count, 3,
                         'Mail.send() should be call exactly 3 times.')
        self.assertRegex(logs.output[0],
                         'Failed to send message with subject "One" 3 times.  Giving up.')

    def test_fail_and_then_pass(self):
        """The first send fails, then the subsequent ones pass."""
        mail = MailMockFailPass()
        check_internet_connection = CheckInternetConnectionMock()
        mailqueue = MailQueue(mail, check_internet_connection)
        mailqueue.add(Message('One', 'BodyOne'))
        # The first time, send will raise an exception.
        mailqueue.send()

        # The second time, send will pass.
        mailqueue.send()

        # The third time, there is nothing in the queue.  So send should be called exactly twice.
        mailqueue.send()
        self.assertEqual(mail.send_call_count, 2)

    def test_internet_down_and_up(self):
        """Tests the Internet being down for awhile, and then comes back up."""
        mail = Mock(Mail)
        check_internet_connection = CheckInternetConnectionMock([False, False, False, False, False, True])
        # noinspection PyTypeChecker
        mailqueue = MailQueue(mail, check_internet_connection)
        mailqueue.add(Message('One', 'BodyOne'))

        # Send the message 5 times.  The actual mail.send() method should
        # not have been called because the Internet is down.
        for count in range(0, 5):
            mailqueue.send()
        self.assertEqual(mail.send.call_count, 0)

        # On the 6th call, the Internet is back up and mail gets sent.
        mailqueue.send()
        self.assertEqual(mail.send.call_count, 1)


class MailMockFailPass(Mail):
    """Fails on the first send, and then passes on the second send."""
    def __init__(self):
        super().__init__('test@mail.com', 'password', ['receiver@mail.com'])
        self.send_call_count = 0

    def send(self, subject, body):
        self.send_call_count += 1
        if self.send_call_count == 1:
            raise MailException('MailMockFailPass')


class CheckInternetConnectionMock(CheckInternetConnection):
    """Mocks CheckInternetConnection class."""
    def __init__(self, connect_results=None):
        """Constructor.

        :param list[bool] connect_results: List of returns that connected() will return.  If None,
            then connected() will always return True.
        """
        super().__init__()
        self.connect_results = connect_results
        self.connect_results_index = 0

    def connected(self):
        """If given, returns the next result in the list."""
        if self.connect_results is None:
            return True
        else:
            return_value = self.connect_results[self.connect_results_index]
            self.connect_results_index += 1
            return return_value


if __name__ == '__main__':
    unittest.main()
