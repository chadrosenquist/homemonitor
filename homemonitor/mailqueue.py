import logging

from homemonitor.mail import MailException


class Message(object):
    """Represents a message in the queue."""
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body
        self.retry_count = 0


class MailQueue(object):
    """Sends email with error handling.

    Place messages into the queue and this class will attempt to send them.

    * If an error, retry a few times.
    * If there is no internet connection, keep checking until connection is restored.

    Example::

        mail = GMail('hello@gmail.com', 'password')
        mailqueue = MailQueue(mail)
        mailqueue.add(Message('hi', 'how are you?'))
        mailqueue.send()

    """
    def __init__(self, mail, retries=3):
        """Constructor

        :param Mail mail: Object used to send the email message.
        :param int retries: Number of times to retry sending a message.
        """
        self.mail = mail
        self.retries = retries
        self.queue = []
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def add(self, message):
        """Adds a message to the queue.

        :param Message message: Message to be sent.
        """
        self.queue.append(message)

    def send(self):
        """Attempts to send the messages in the queue.

        If it fails to send email, increment the retry count
        and add it back to the queue if less than the threshold.
        """
        failed_queue = []
        for message in self.queue:
            try:
                self.mail.send(message.subject, message.body)
            except MailException:
                message.retry_count += 1
                if message.retry_count < self.retries:
                    failed_queue.append(message)
        self.queue = failed_queue
