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

import os, time

try:
    import RPi.GPIO as GPIO
    test_run = False
except:
    test_run = True
    TRIGGER_DELAY = 10

from pi_doorbell import configure, notify, webserver

from pi_doorbell import logger
import logging
log = logger.get_logger("service")
def _log(message, level="info"):
    if level == "debug":
        log.debug(message);
    elif level == "info":
        log.info(message);
    elif level == "warning":
        log.warning(message);

class Service():
    def __init__(self):
        # Fetch configuration
        self.Configure                  = configure.Configure();
        self.config                     = self.Configure.getConfig();
        self.debug                      = False

        # Configure logger
        log_level                       = logging.INFO
        if self.config['General']['debugging']: # Force debugging if set to true in user config
            self.debug                  = True
            log_level                   = logging.DEBUG
        logger.set_log_handler_config(log_level)

        # Setup notifications to chromecast devices
        self.notify                     = notify.Notify(config=self.config, debug=self.debug);

        # Configure the GPIO to monitor. If not GPIO is available, service will switch to "test_run" mode which will trigger every TRIGGER_DELAY sec.
        self.use_pin                    = int(self.config['General']['use_pin']);
        self.pin_pull_up                = int(self.config['General']['pin_pull_up']);
        self.post_trigger_delay         = int(self.config['General']['post_trigger_delay']);
        self.pin_trigger                = "LOW";
        self.pin_default                = "HIGH";
        self.pin_default_value          = 1
        if not test_run:
            GPIO.setmode(GPIO.BOARD);
            if self.pin_pull_up:
                GPIO.setup(self.use_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP);
                self.pin_trigger        = "HIGH";
                self.pin_default        = "LOW";
                self.pin_default_value  = 0;
            else:
                GPIO.setup(self.use_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);
                self.pin_trigger        = "LOW";
                self.pin_default        = "HIGH";
                self.pin_default_value  = 1;
        
        # Configure default web server status
        self.web_server      = None;
        self.doorbell        = webserver.DoorbellStatus()
        self.doorbell.status = 'off';

    def handle_event(self):
        string = self.Configure.returnRandomString();
        _log('Sending notification: "%s"' % string);
        self.notify.send(string);
        self.set_doorbell_status('on');

    def reset_event(self):
        self.set_doorbell_status('off');
            
    def run_webserver(self):
        if not self.web_server:
            self.web_server = webserver.HttpServer(config=self.config)
            self.web_server.start()
            self.web_server.setDoorbellStatus('off')
            
    def stop_webserver(self):
        self.web_server.stop();
        _log("Web Server Stopped");
            
    def set_doorbell_status(self, status):
        webserver.DoorbellStatus.status = status
        _log("Setting web status to: %s" % status);

    def run(self):
        old_state   = 1;
        state       = 0;
        # Check if this is run a as a test server or on a raspi
        if test_run:
            _log("Service running in test mode.");
            count = 0;
        else:
            _log("Service running.");

        # Start the webserver
        if not self.Configure.args.no_web_server:
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
                    if state == self.pin_default_value:
                        if old_state != state:
                            old_state = state;
                            _log("Input was reset back to default value: %s" % self.pin_default);
                            self.reset_event();
                    else:
                        if old_state != state:
                            old_state = state;
                            _log("Input was set to %s" % self.pin_trigger);
                            self.handle_event();
                            if self.post_trigger_delay:
                                post_trigger_delay_count = 0;
                                _log("Executing a post trigger delay of %s seconds" % self.post_trigger_delay);
                                while post_trigger_delay_count != self.post_trigger_delay: # Loop to add delay while processing state change
                                    time.sleep(1);
                                    post_trigger_delay_count += 1;
                            while state != self.pin_default_value: # Loop while state still held high
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
            self.stop_webserver()



def main():
    service = Service();
    service.run();


if __name__ == '__main__':
    main();
