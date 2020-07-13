#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     03 February, 2018 (16:30:18)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (13:02:05)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################


import os
import socket
import hashlib
import pychromecast
from gtts import gTTS

import logging
from pi_doorbell import logger
log = logger.get_logger("notify")
def _log(message, level="info"):
    if level == "debug":
        log.debug(message);
    elif level == "info":
        log.info(message);
    elif level == "warning":
        log.warning(message);

class Notify():
    def __init__(self, config, debug=False):
        self.debug          = debug;
        self.config         = config;
        self.chromecasts    = [];

    def log(self, string):
        if self.debug:
            try:
                _log( string );
            except UnicodeEncodeError:
                bom = str(codecs.BOM_UTF8, 'utf8')
                _log( string.replace(bom, '') );
            except:
                pass

    def discover_devices(self):
        self.log("Discovering ChromeCast devices...");
        chromecasts, browser = pychromecast.get_chromecasts()
        pychromecast.discovery.stop_discovery(browser)
        for cast in chromecasts:
            self.chromecasts.append(cast)
            self.log("Found device: %s" % cast.device.friendly_name);

    def send(self, message = ""):
        port         = self.config['WebServer']['port'];
        cache_dir    = self.config['WebServer']['mp3_cache'];
        tts_language = self.config['WebServer']['tts_language'];

        # Check if we have a cached copy of this sound-byte
        mp3_file  = hashlib.md5(message.encode('utf-8')).hexdigest() + "_" + tts_language + ".mp3";
        mp3_path  = os.path.join(cache_dir, mp3_file);
        if not os.path.isfile(mp3_path):
            # No cached copy, create a new one with Google's TTS API
            self.log('Generating MP3: %s' % mp3_file);
            tts = gTTS(text=message, lang=tts_language);
            tts.save(mp3_path);
        else:
            # Found a cached copy
            self.log('Reusing MP3: %s' % mp3_file);

        # Get the IP address of this server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        s.connect(("8.8.8.8", 80));
        socket_name = s.getsockname();
        s.close();
        if not socket_name:
            return False;

        # Create link to internal file server
        if port:
            url = 'http://%s:%s/%s' % (socket_name[0], port, mp3_file);
        else:
            url = 'http://%s/%s' % (socket_name[0], mp3_file);
        self.log('MP3 url: %s' % url);

        # Send url to chromecast devices
        self.chromecast(url);

        return True;
    
    def chromecast(self, url):
        chromecast_config = self.config['ChromeCast']
        if not chromecast_config.get('enable_chromecast', True):
            self.log("(ChromeCast) Device not enabled");
            return;
        filters_by_device_name = chromecast_config['filters_by_device_name'];
        filters_by_model       = chromecast_config['filters_by_model'];
        device_names           = [x.strip() for x in filters_by_device_name.split(',')];
        model_names            = [x.strip() for x in filters_by_model.split(',')];
        if not self.chromecasts:
            self.discover_devices();
        receivers_list = [];
        for cast in self.chromecasts:
            send = False;
            if cast.device.model_name in model_names:
                send = True;
            if cast.device.friendly_name in device_names:
                send = True;

            if send:
                cast.wait()
                cast.media_controller.play_media(url, 'audio/mp3')
        self.log("Message Sent to ChromeCast device(s)");
        return;


