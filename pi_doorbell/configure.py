#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (josh@streamingtech.tv)
#   Date:                     04 February, 2018 (09:02:57)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (10:53:08)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################

import ConfigParser

import os, random




NOTIFICATION_STRINGS = [
    "There is someone at the {!door_name} door.",
    "Oh my! You have a visitor. How exciting!",
    "Hooray! We have company. I do love a social gathering. Please introduce me wont you {!family_name}.",
    "{!family_name}, I have detected an unknown entity at the {!door_name} door.",
]

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

class Configure():
    def __init__(self, debug):
        self.debug      = debug;
        self.Config     = ConfigParser.ConfigParser();
        self._config    = {}

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
        home            = os.path.expanduser("~");
        conf_file       = os.path.join(home, '.pi_doorbell', 'config.ini');
        conf_dir        = os.path.dirname(conf_file);
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir);
        for section in DEFAULT_CONFIG.keys():
            self.Config.add_section(section);
            for key in DEFAULT_CONFIG[section].keys():
                self.Config.set(section, key, DEFAULT_CONFIG[section][key]);
        with open(conf_file, 'w') as f:
            self.Config.write(f);

    def getConfig(self):
        self._config    = DEFAULT_CONFIG;
        home            = os.path.expanduser("~");
        conf_file       = os.path.join(home, '.pi_doorbell', 'config.ini');
        if os.path.isfile(conf_file):
            self.Config.read(conf_file);
            sections = self.Config.sections();
            for x in sections:
                    configdic = self.configSectionMap(x);
                    self._config[x] = configdic;
        else:
            self.writeDefaultConfig();
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