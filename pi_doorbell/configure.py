#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     04 February, 2018 (09:02:57)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (13:02:08)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################

import configparser

import sys, os, random

from .version import __version__



NOTIFICATION_STRINGS = [
    "There is someone at the {!door_name} door.",
    "Oh my! You have a visitor. How exciting!",
    "Hooray! We have company. I do love a social gathering. Please introduce me will you {!family_name}.",
    "{!family_name}, I have detected an unknown entity at the {!door_name} door.",
    "{!family_name}, there seems to be a fello human at our {!door_name} door.",
    "{!family_name}, there is someone at the door. I would get it myself, but unfortunately Google has not designed me with mobility in mind.",
    "Knock knock! Who's there? Well why don't you go to the {!door_name} door and see.",
]

CONFIG_LOCATION = os.path.join('/', 'etc', 'pi_doorbell', 'config.ini');

DEFAULT_CONFIG = {
    'Args': {},
    'General': {
        'debugging': False,
        'use_pin': '26',
        'pin_pull_up': True,
        'post_trigger_delay': '1',
        'door_name': '',
        'family_name': 'Humans'
    },
    'WebServer': {
        'host': '0.0.0.0',
        'port': '8001',
        'mp3_cache': '/tmp/pi_doorbell',
        'tts_language': 'en-NZ'
    },
    'ChromeCast': {
        'filters_by_device_name': '',
        'filters_by_model': ''
    }
}

try:
    from argparse import ArgumentParser as ArgParser
    from argparse import SUPPRESS as ARG_SUPPRESS
    PARSER_TYPE_INT = int
    PARSER_TYPE_STR = str
except ImportError:
    from optparse import OptionParser as ArgParser
    from optparse import SUPPRESS_HELP as ARG_SUPPRESS
    PARSER_TYPE_INT = 'int'


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

def parse_args():
    """Function to handle building and parsing of command line arguments"""
    description = (
        'Raspberry Pi Doorbell Notifications Service for Home-Assistant '
        '\n'
        '--------------------------------------------------------------'
        '\n');
    parser = ArgParser(description=description)
    try:
        parser.add_argument = parser.add_option;
    except AttributeError:
        pass

    parser.add_argument('-v', '--version', action='store_true',
                        help='Show the version number and exit');
    parser.add_argument('-d', '--debug', dest='debugging', action='store_true',
                        help='Run with debugging enabled', default=False);
    parser.add_argument('-w', '--no-web-server', dest='no_web_server', action='store_true',
                        help='Disable the web server', default=False);
    parser.add_argument('-s', '--no-service', dest='no_service', action='store_true',
                        help='Disable the daemon service', default=False);
    parser.add_argument('-c', '--config_file', type=PARSER_TYPE_STR,
                        help='Specify a config file location. Default is "/etc/pi_doorbell/config.ini"');

    options = parser.parse_args();
    if isinstance(options, tuple):
        args = options[0];
    else:
        args = options;
    # Print the version and exit
    if args.version:
        try:
            print(__version__);
        except:
            print('Unknown Version');
        sys.exit(0);
    return args


class Configure():
    def __init__(self, debug=False):
        self.debug      = debug;
        self.Config     = configparser.ConfigParser();
        self._config    = {};
        self.args       = parse_args();
        self._config['Args'] = self.args;
        if self.args.debugging:
            self.debug  = True;
        self.conf_file  = CONFIG_LOCATION;
        if self.args.config_file:
            self.conf_file = self.args.config_file;


    def configSectionMap(self,section):
        dict1   = DEFAULT_CONFIG[section];
        options = self.Config.options(section);
        for option in options:
            try:
                value = self.Config.get(section, option);
                if value.lower() == 'true':
                    value = True;
                elif value.lower() == 'false':
                    value = False;
                dict1[option] = value;
            except:
                _log("exception on %s!" % option);
                dict1[option] = None;
        return dict1;

    def writeDefaultConfig(self):
        conf_dir        = os.path.dirname(self.conf_file);
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir);
        for section in list(DEFAULT_CONFIG.keys()):
            self.Config.add_section(section);
            for key in list(DEFAULT_CONFIG[section].keys()):
                self.Config.set(section, key, DEFAULT_CONFIG[section][key]);
        with open(self.conf_file, 'w') as f:
            self.Config.write(f);

    def getConfig(self):
        self._config    = DEFAULT_CONFIG;
        if os.path.isfile(self.conf_file):
            self.Config.read(self.conf_file);
            sections = self.Config.sections();
            for x in sections:
                    configdic = self.configSectionMap(x);
                    self._config[x] = configdic;
        else:
            self.writeDefaultConfig();
        if self.debug: # Force debugging if debugging flag was passed
            self._config['General']['debugging'] = True;
        return self._config;

    def formatString(self, string):
        for replacement in ['family_name','door_name']:
            string = string.replace('{!%s}'%replacement, self._config['General'][replacement]);
        return string;

    def returnRandomString(self):
        return_string = random.choice(NOTIFICATION_STRINGS);
        return self.formatString(return_string);




if __name__ == '__main__':
    config = Configure();
    _log(config.getConfig());
    _log(config.returnRandomString());