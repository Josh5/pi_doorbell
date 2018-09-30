#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     04 February, 2018 (08:14:45)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (13:03:04)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################

import os, time, socket, threading
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

try:
    import RPi.GPIO as GPIO
    test_run = False
except:
    test_run = True
    TRIGGER_DELAY = 10

from . import configure, notify

import logging
logging.basicConfig(level=logging.DEBUG)

def _log(message, level="info"):
    import logging
    message = "Pi Doorbell - %s" % message
    if level == "debug":
        logging.debug(message);
    elif level == "info":
        logging.info(message);
    elif level == "warning":
        logging.warning(message);


class Service():
    def __init__(self):
        # Fetch configuration
        self.Configure  = configure.Configure();
        self.config     = self.Configure.getConfig();
        self.debug      = False
        if self.config['General']['debugging']: # Force debugging if set to true in user config
            self.debug  = True

        # Setup notifications to chromecast devices
        self.notify     = notify.Notify(config=self.config, debug=self.debug);

        # Configure the GPIO to monitor. If not GPIO is available, service will switch to "test_run" mode which will trigger every TRIGGER_DELAY sec.
        self.use_pin    = int(self.config['General']['use_pin']);
        if not test_run:
            GPIO.setmode(GPIO.BOARD);
            GPIO.setup(self.use_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);
        self.web_server = None;

    def logging(self, message):
        if self.debug:
            timestr = time.strftime("%Y%m%d-%H%M%S");
            message = "[%s] %s" % (timestr, message);
            _log(message);

    def handle(self):
        string = self.Configure.returnRandomString();
        self.logging('Sending notification: "%s"' % string);
        self.notify.send(string);
            
    def setup_webserver_dir(self):
        cache_dir = self.config['WebServer']['mp3_cache'];
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir);
        os.chdir(cache_dir);
            
    def run_webserver(self):
        host = self.config['WebServer']['host'];
        port = int(self.config['WebServer']['port']);
        if not self.web_server:
            web_server = HTTPServer((host, port), SimpleHTTPRequestHandler);
            self.web_server = threading.Thread(target=web_server.serve_forever);
            self.web_server.daemon = True
            self.web_server.start();
            self.logging("Web Server Started - %s:%s" % (host, port));
            
    def stop_webserver(self):
            self.web_server.shutdown()
            self.web_server.server_close()
            self.logging("Web Server Stopped - %s:%s" % (host, port));

    def run(self):
        old_state   = 1;
        state       = 0;
        # Check if this is run a as a test server or on a raspi
        if test_run:
            self.logging("Service running in test mode.");
            count = 0;
        else:
            self.logging("Service running.");

        # Start the webserver
        if not self.Configure.args.no_web_server:
            self.setup_webserver_dir();
            self.run_webserver();

        # Run the service
        self.notify.discover_devices();
        try:
            while True:
                if not self.Configure.args.no_service:
                    if test_run:
                        if count > TRIGGER_DELAY and count % TRIGGER_DELAY == 0:
                            state = 0;
                        else:
                            state = 1;
                        count += 1;
                    else:
                        state = GPIO.input(self.use_pin);
                    if state:
                        if old_state != state:
                            old_state = state;
                            self.logging("Input was set to HIGH");
                    else:
                        if old_state != state:
                            old_state = state;
                            self.logging("Input was set to LOW");
                            self.handle();
                            while not state: # Loop while state still held high
                                if test_run:
                                    if count % 10 == 0:
                                        state = 0;
                                    else:
                                        state = 1;
                                else:
                                    state = GPIO.input(self.use_pin)
                                time.sleep(1);
                time.sleep(1);
        except KeyboardInterrupt:
            pass



def main():
    service = Service();
    service.run();


if __name__ == '__main__':
    main();
