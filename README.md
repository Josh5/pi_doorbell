# pi_doorbell

The setup scripts and run scripts for running my DIY doorbell notifications from a raspberry pi

This is designed to run on a Debian based operating system. I used Rasbian with a Raspberry Pi B. You may need to change a few things in order to get it working with other Raspberry Pi models.


# Setup:

#### Dependencies:

Start by install all dependencies first.
```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
    openssh-server \
    git \
    python2.7 \
    python-rpi.gpio \
    python-pip \
    python3 \
    python3-rpi.gpio \
    python3-venv \
    python3-pip \
    python3-urllib3
```

---



#### Home-Assistant:


##### Create Home-Assistant environment:

Home-Assistant should be run as a separate user in a python virtual env.

For more information see [HERE](https://home-assistant.io/docs/installation/virtualenv/)

```
sudo useradd -rm homeassistant
cd /srv
sudo mkdir homeassistant
sudo chown homeassistant:homeassistant homeassistant
sudo su -s /bin/bash homeassistant
cd /srv/homeassistant
python3 -m venv .
source bin/activate
```


##### Install Home-Assistant:
```
python3 -m pip install wheel
python3 -m pip install homeassistant
```

Now run Home-Assistant for the first time.

```
hass
```


> __Note:__ 
> This make take a while to execute the first time so just leave it to set everything up. On a RasPi B it took about 10 mins



##### Add auto-startup script:

Create a new systemd unit for the Home-Assistant by running this command:
```
sudo nano /etc/systemd/system/home-assistant@homeassistant.service
```

Populate the unit file with this:

```
[Unit]
Description=Home Assistant
After=network-online.target

[Service]
Type=simple
User=%i
ExecStart=/srv/homeassistant/bin/hass -c "/home/homeassistant/.homeassistant"

[Install]
WantedBy=multi-user.target
```

Reload the systemd service and then enable the service to run it on start
```
sudo systemctl --system daemon-reload
sudo systemctl enable home-assistant@homeassistant.service
```


Now when your Pi starts you will have Home-Assistant running on port 8123.

---



#### Pi Doorbell Notifications Service:


##### Install Pi Doorbell Notifications:

Start by cloning this repo or downloading the latest source.

```
git clone https://github.com/Josh5/pi_doorbell.git
```


Now install the python module.

```
cd pi_doorbell
python ./setup.py build
sudo python ./setup.py install
```


##### Add auto-startup script:

Ideally, we want this to run on startup.

First find the location where the pi_doorbell script was installed.

```
which pi_doorbell
```

You should see an output something like this: " */usr/local/bin/pi_doorbell* "

So we will create another systemd unit for the Pi Doorbell Notifications by running this command:
```
sudo nano /etc/systemd/system/pi-doorbell.service
```

Populate the unit file with this:

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

Reload the systemd service and then enable the service to run it on start
```
sudo systemctl --system daemon-reload
sudo systemctl enable pi-doorbell.service
```