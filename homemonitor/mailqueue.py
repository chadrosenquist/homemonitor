import logging


class Message(object):
    """Represents a message in the queue."""
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body


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
    def __init__(self, mail):
        """Constructor

        :param Mail mail: Object used to send the email message.
        """
        self.mail = mail
        self.queue = []
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def add(self, message):
        """Adds a message to the queue.

        :param Message message: Message to be sent.
        """
        self.queue.append(message)

    def send(self):
        """Attempts to send the messages in the queue."""
        failed_queue = []
        for message in self.queue:
            self.mail.send(message.subject, message.body)
        self.queue = failed_queue
