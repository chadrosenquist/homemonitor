import unittest
from unittest.mock import Mock, MagicMock

from homemonitor.mail import Mail, MailException
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



if __name__ == '__main__':
    unittest.main()
