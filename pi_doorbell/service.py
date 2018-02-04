#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (josh@streamingtech.tv)
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

import os, time

try:
    import RPi.GPIO as GPIO
    test_run = False
except:
    test_run = True

import configure, notify

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
    def __init__(self, debug):
        self.debug      = debug
        self.Configure  = configure.Configure(debug=self.debug);
        self.config     = self.Configure.getConfig();
        if self.config['General']['debugging']: # Force debugging if set to true in user config
            self.debug  = True
        self.notify     = notify.Notify(config=self.config, debug=self.debug);
        self.use_pin    = int(self.config['General']['use_pin']);
        if not test_run:
            GPIO.setmode(GPIO.BOARD);
            GPIO.setup(self.use_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);

    def logging(self, message):
        if self.debug:
            timestr = time.strftime("%Y%m%d-%H%M%S");
            message = "[%s] %s" % (timestr, message);
            _log(message);

    def handle(self):
        string = self.Configure.returnRandomString();
        self.logging("Sending notification %s" % string);
        self.notify.send(string);

    def run(self):
        old_state   = 1;
        state       = 0;
        if test_run:
            self.logging("Service running in test mode.");
            count = 0;
        else:
            self.logging("Service running.");
        while True:
            if test_run:
                if count > 10 and count % 10 == 0:
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



def main():
    service = Service(debug=False);
    service.run();


if __name__ == '__main__':
    main();
