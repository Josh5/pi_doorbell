#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     12 July, 2020 (20:42:17)
#   Last Modified by:         Josh.5 
#                             on 12 July, 2020 (20:42:17)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################


from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import argparse
import re
import cgi
import json
import os

import logging
from pi_doorbell import logger
log = logger.get_logger("webserver")
def _log(message, level="info"):
    if level == "debug":
        log.debug(message);
    elif level == "info":
        log.info(message);
    elif level == "warning":
        log.warning(message);


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DoorbellStatus(object, metaclass=SingletonType):
    status = None


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    #def __init__(self, debug=False):
    #    self.debug = debug;

    def log(self, string):
        try:
            _log( '[HTTPRequestHandler]: %s' % string );
        except UnicodeEncodeError:
            bom = str(codecs.BOM_UTF8, 'utf8')
            _log( '[HTTPRequestHandler]: %s' % string.replace(bom, '') );
        except:
            pass

    def do_GET(self):
        self.log(self.path)
        if None != re.search('/api/v1/status/*', self.path):
            recordID = self.path.split('/')[-1]
            if DoorbellStatus.status:
                doorbell_status_json = json.dumps({'return_value': DoorbellStatus.status})
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.log("Current doorbell status - %s" % doorbell_status_json)
                self.wfile.write(doorbell_status_json.encode(encoding='utf_8'))
            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            super().do_GET()
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)

class HttpServer():
    def __init__(self, config):
        self.config = config;
        self.host   = self.config['WebServer']['host'];
        self.port   = int(self.config['WebServer']['port']);
        self.server = ThreadedHTTPServer((self.host, self.port), HTTPRequestHandler)
            
    def setup_webserver_dir(self):
        cache_dir = self.config['WebServer']['mp3_cache'];
        # Create path if it does not yet exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir);
        # Change to the path for serving http requests
        os.chdir(cache_dir);

    def start(self):
        self.setup_webserver_dir()
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def setDoorbellStatus(self, status):
        DoorbellStatus.status = status

    def stop(self):
        self.server.shutdown()
        self.waitForThread()



if __name__ == '__main__':
    config = {
        'WebServer' : {
            'host': '0.0.0.0',
            'port': '8001',
        }
    }
    server = HttpServer(config)
    server.setDoorbellStatus('off')
    server.start()
    server.waitForThread()
