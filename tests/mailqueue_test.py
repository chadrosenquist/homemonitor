import unittest
from unittest.mock import Mock
from loggingtestcase import capturelogs

from homemonitor.mail import MailException
from homemonitor.mailqueue import MailQueue, Message


class MailQueueTest(unittest.TestCase):
    def test_second_two_messags(self):
        """Tests sending two messages, with a mock.

        The send method should be called twice, once for each message.
        """
        mail = Mock()
        mailqueue = MailQueue(mail)
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
        mail = Mock()
        mail.send = Mock(side_effect=MailException)
        mailqueue = MailQueue(mail, retries=3)
        mailqueue.add(Message('One', 'BodyOne'))
        for count in range(0, 5):
            mailqueue.send()
        self.assertEqual(mail.send.call_count, 3,
                         'Mail.send() should be call exactly 3 times.')
        self.assertRegex(logs.output[0],
                         'Failed to send message with subject "One" 3 times.  Giving up.')

    def test_fail_and_then_pass(self):
        """The first send fails, then the subsequent oncs pass."""
        mail = MailMockFailPass()
        mailqueue = MailQueue(mail)
        mailqueue.add(Message('One', 'BodyOne'))
        # The first time, send will raise an exception.
        mailqueue.send()

        # The second time, send will pass.
        mailqueue.send()

        # The third time, there is nothing in the queue.  So send should be called exactly twice.
        mailqueue.send()
        self.assertEqual(mail.send_call_count, 2)


class MailMockFailPass(object):
    """Fails on the first send, and then passes on the second send."""
    def __init__(self):
        self.send_call_count = 0

    # noinspection PyUnusedLocal,PyUnusedLocal
    def send(self, subject, body):
        self.send_call_count += 1
        if self.send_call_count == 1:
            raise MailException('MailMockFailPass')


if __name__ == '__main__':
    unittest.main()
