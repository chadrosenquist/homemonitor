import logging

from homemonitor.mail import MailException


class Message(object):
    """Represents a message in the queue."""
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body
        self.retry_count = 0

    def __eq__(self, other):
        return self.subject == other.subject and self.body == other.body

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.subject, self.body)


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
    def __init__(self, mail, check_internet_connection, retries=3):
        """Constructor

        :param homemonitor.mail.Mail mail: Object used to send the email message.
        :param homemonitor.internetconnection.CheckInternetConnection check_internet_connection: CheckInternetConnection
        :param int retries: Number of times to retry sending a message.
        """
        self.mail = mail
        self.check_internet_connection = check_internet_connection
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

        If there is no Internet connection, do not even attempt to send email out.

        If it fails to send email, increment the retry count
        and add it back to the queue if less than the threshold.

        If failed to send self.retries times (i.e. 3), then stop trying
        to send the message and log an error.
        """
        if not self.check_internet_connection.connected():
            return

        failed_queue = []
        for message in self.queue:
            try:
                self.mail.send(message.subject, message.body)
            except MailException:
                message.retry_count += 1
                if message.retry_count < self.retries:
                    failed_queue.append(message)
                else:
                    self.logger.error('Failed to send message with subject "{0}" {1} times.  '
                                      'Giving up.'.format(message.subject,
                                                          self.retries))
        self.queue = failed_queue
