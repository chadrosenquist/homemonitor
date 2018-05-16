# Home Monitor for Raspberry Pi
Provides a way to monitor your home with your Raspberry Pi.
Connect an Adafruit temperature sensor and it will send email
when it detects the temperature is too low (furnace broke).


# Installation
Currently, Home Monitor is installed from Git and run directly from the Git repository.
For example:
```
cd /home/pi/git
git clone git@github.com:chadrosenquist/homemonitor.git
cd homemonitor
```

Create a 'home' directory for home monitor (it will be used later):
```
mkdir /home/pi/homemonitor
```

# Install Adafruit Driver
The temperature sensor is from Adafruit.

[AM2302 on Amazon](https://www.amazon.com/gp/product/B01N9BA0O4/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1)

[Adafruit Software Page](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated)

To install their driver:
```
cd /home/pi/git
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo apt-get update
sudo apt-get install build-essential python-dev python-openssl
sudo python3 setup.py install
```

To test on a Raspberry Pi with an AM2302 sensor connected to GPIO #4, execute:
```
cd /home/pi/git/Adafruit_Python_DHT/examples
sudo ./AdafruitDHT.py 2302 4
```

# Configuration File
The is a sample configuration file located at:
```
/home/pi/git/homemonitor/homemonitor/homemonitor.ini-TEMPLATE
```

Copy it to the home directory:
```
cp /home/pi/git/homemonitor/homemonitor/homemonitor.ini-TEMPLATE /home/pi/homemonitor/.homemonitor.ini
chmod 600 /home/pi/homemonitor/.homemonitor.ini
```


### Mail
Home Monitor uses this information to send out an email if it detects problems.
```
[mail]
user=sender@gmail.com
password=<application password>
receivers=receiver1@gmail.com, receiver2@gmail.com
server=smtp.gmail.com
port=587
```

Specify your `user` and `password` for the email account that will send mail.
Give it a list of who will receive the emails, separated by a comma.
Set your SMTP server and port.

### Internet
Home Monitor checks if it has a connection to the Internet.
```
server=google.com
port=80
timeout_in_seconds=20
```

The `server:port` will be pinged to verify if there is an Internet connection.
`timeout_in_seconds` is how many sections to wait before timing out the ping.
The default values do not need to be modified.

### Event Loop
Home Monitor continually loops and polls the sensors.

```
[eventloop]
poll_interval_in_seconds=900
```

`poll_interval_in_seconds` is how many seconds per loop, defaulting to 900 seconds
(15 minutes).

### Temperature Sensors
Defines the temperature sensors connected.  The section name is is the format:
`[TemperatureSensor_<name>]`.  Each sensor is given a name.

```
[TemperatureSensor_Basement]
temperature=50
gpio=4
model=AM2302
```

In the above example, the sensors name is `Basement`.  It generates an alarm
when the temperature goes below `50` degrees Fahrenheit.
It is connected to GPIO port number `4` and is Adafruit model `AM2302`.

### Logging
This section allows control of the logging.  For more details, see
[Python3 Logging](https://docs.python.org/3/howto/logging.html).

The point of interest is the log file location:
```
[handler_fileHandler]
args=('/home/pi/homemonitor/homemonitor.log', 'a')
```

If Home Monitor is installed in a directory other than
`/home/pi/homemonitor`, this section needs to be updated.

# Test Run
Once the config file is setup, it is time to do a test run:
```
cd /home/pi/git/homemonitor
sudo python3 homemonitor --test
INFO: 2018-05-15 21:07:12,080: Created TemperatureSensor TemperatureSensor/Basement with
    temperature threshold of 50 degrees, connected to GPIO 4, and model AM2302.
Sending test email to ['your_email@gmail.com']...
INFO: 2018-05-15 21:07:13,874: Sent email to ['your_email@gmail.com'] with subject
    "Test email from homemonitor.".
Done.  Check your inbox.
```

The test run will display messages about each sensor connected.
Then it will send a test email.

# Command Line Options
```
python homemonitor --help
python homemonitor [option]
    -h|--help: Print help.
    -v|--version: Version
    -t|--test: Send a test email and test all sensors.
    -c=|--config=: Give location of configuration file.
        Defaults to ~/homemonitor/.homemonitor.ini
```

# Start as a Service
Have Home Monitor automatically startup using `systemd`.

```
sudo cp /home/pi/git/homemonitor/homemonitor/homemonitor.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/homemonitor.service 

sudo systemctl daemon-reload
sudo systemctl enable homemonitor.service

sudo reboot
```

When the system comes back up, verify it is running by the log file:
`/home/pi/homemonitor/homemonitor.log`

# Roadmap
Here is the current roadmap for future releases:
* 0.1 : TemperatureSensor
* 0.2 : WaterSensor
* 0.3 : Better install
* 0.4 : Light indicating homemonitor is running.
