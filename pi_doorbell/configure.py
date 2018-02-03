#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (josh@streamingtech.tv)
#   Date:                     04 February, 2018 (09:02:57)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (12:21:10)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################

import ConfigParser

import sys, os, random




NOTIFICATION_STRINGS = [
    "There is someone at the {!door_name} door.",
    "Oh my! You have a visitor. How exciting!",
    "Hooray! We have company. I do love a social gathering. Please introduce me wont you {!family_name}.",
    "{!family_name}, I have detected an unknown entity at the {!door_name} door.",
]

CONFIG_LOCATION = os.path.join('/', 'etc', 'pi_doorbell', 'config.ini');

DEFAULT_CONFIG = {
    'General': {
        'debugging': False,
        'use_pin': '26',
        'door_name': '',
        'family_name': 'Humans'
    },
    'HomeAssistant': {
        'host': 'localhost',
        'port': '8123',
        'api_password': False,
        "media_players":False
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
        self.Config     = ConfigParser.ConfigParser();
        self._config    = {};
        self.args       = parse_args();
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
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option);
            except:
                print("exception on %s!" % option);
                dict1[option] = None;
        return dict1;

    def writeDefaultConfig(self):
        conf_dir        = os.path.dirname(self.conf_file);
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir);
        for section in DEFAULT_CONFIG.keys():
            self.Config.add_section(section);
            for key in DEFAULT_CONFIG[section].keys():
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
    config = Configure(debug=True);
    print config.getConfig();
    print config.returnRandomString();