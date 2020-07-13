# pi_doorbell

The setup scripts and run scripts for running my DIY doorbell notifications from a raspberry pi

This is designed to run on a Debian based operating system. I used Rasbian with a Raspberry Pi B. You may need to change a few things in order to get it working with other Raspberry Pi models.


## Setup:

### Install dependencies:

Start by install all dependencies first.
```
sudo apt-get install -y \
    git \
    python3 \
    python3-rpi.gpio \
    python3-pip

sudo python3 -m pip install -r requirements.txt
```

---



### Build and install from source:

Clone this repo or download the latest source.

eg.

```
git clone https://github.com/Josh5/pi_doorbell.git /opt/pi_doorbell
```


Run the following commands to install the python module

```
cd /opt/pi_doorbell
python3 ./setup.py build
sudo python3 ./setup.py install
```



### Configure pi_doorbell

Start by copying the default config file. 

```
sudo mkdir -p /etc/pi_doorbell
sudo cp -f /opt/pi_doorbell/config/config.ini.sample /etc/pi_doorbell/config.ini
```

Once this is installed, you can edit it to suit your needs.

```
sudo nano /etc/pi_doorbell/config.ini
```



### Create systemd unit

Ideally, we want this to run on startup.

First find the location where the pi_doorbell script was installed.

```
which pi_doorbell
```

You should see an output something like this: " */usr/local/bin/pi_doorbell* "

So we will create systemd unit for the Pi Doorbell Notifications by running this command:
```
sudo nano /lib/systemd/system/pi_doorbell.service
```

Populate the unit file with the following text (changing the path to pi_doorbell according to what was returned above):

```
[Unit]
Description=Pi Doorbell Notifications
After=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/pi_doorbell -d
TimeoutSec=30
Restart=always
RestartSec=10
StartLimitInterval=350
StartLimitBurst=10

[Install]
WantedBy=multi-user.target

```

Enable the newly created systemd unit
```
sudo systemctl enable pi_doorbell.service
```

Now the Pi Doorbell Notifications service will run whenever the RaspberryPi starts.

To start it now without needing to reboot, run:
```
sudo systemctl restart pi_doorbell
```



## Update:

To update, `cd` to the path where the pi_doorbell project was cloned.

Run these commands:

```
cd /opt/pi_doorbell

git checkout master .
git pull origin master

python3 ./setup.py build
sudo python3 ./setup.py install
```

Restart the process to have changes come into effect
```
sudo systemctl restart pi_doorbell
```



## Debugging

If you run this as a systemd unit, you can tail the logs using `journalctl`
```
journalctl -u pi_doorbell -f
```

If you want to see more info, then edit the config file in `/etc/pi_doorbell/config.ini`, setting `debugging = true`.

