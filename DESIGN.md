# Design
`cli.py`, function `main()` is the entry point.  `main()` does:

* Handle command line options.
* Read config file.
* Set up logging.
* Create objects from config file.
* If in test mode, send out email and verify sensors are working.
* Loop forever.

### `__main__.py`
This module allows Home Monitor to be run as a package.
It sets the `sys.path` and invokes `homemonitor.cli.main()`.

### `mail.py`
APIs for sending email.

### `mailqueue.py`
Queues up emails to be sent.  Provides extra error handling and robustness.
If an email fails to be sent, retries a few times in case of intermittent issues.
If the Internet is down, `mailqueue.py` will continue re-trying to send
email until the Internet is back up again.

### `internetconnection.py`
Checks if the connection to the Internet is currently up or down.

### `sensor.py`
Base class for all sensors.

### `temperaturesensor.py`
Provides hardware support for Adafruit_DHT temperature/humidity sensors.

### `eventloop.py`
Loops forever.  Each loop, checks the status of each sensor
and send out email if the alarm or hardware status changed.

### Other Design Notes
* Most objects have a normal constructor, `__init__()` and a constructor
that reads the object from a configuration file, `from_config()`.
* Email is only sent when alarm or hardware failure status changes.
For example, when the temperature alarm goes on, one email is sent.
If it remains on, additional emails are not sent out.
