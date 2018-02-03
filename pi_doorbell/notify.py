#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (josh@streamingtech.tv)
#   Date:                     03 February, 2018 (16:30:18)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (10:16:42)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################


import json, time, sys, requests, cookielib


class Notify():
    def __init__(self,config,timeout=20,debug=False):
        self.timeout        = timeout
        self.debug          = debug
        self.config         = config;
        self.BASE_URL       = "http://%s:%s/" % (self.config['HomeAssistant']['host'],self.config['HomeAssistant']['port']);
        self.MEDIA_PLAYERS  = self.config['HomeAssistant']['media_players'];
        self.API_PASSWORD   = self.config['HomeAssistant']['api_password'];
        if not self.API_PASSWORD:
            self.API_PASSWORD = '';
        # Configure session and cookies
        self.http_session   = requests.Session()

        def makearr(tsteps):
            global stemps
            global steps
            stemps = {}
            for step in tsteps:
                stemps[step] = { 'start': 0, 'end': 0 }
            steps = tsteps
        makearr(['init','check'])

        def starttime(typ = ""):
            for stemp in stemps:
                if typ == "":
                    stemps[stemp]['start'] = time.time()
                else:
                    stemps[stemp][typ] = time.time()
        starttime()

    def __str__(self):
        return str(self.url)

    def log(self, string):
        if self.debug:
            try:
                print '[Notify]: %s' % string
            except UnicodeEncodeError:
                bom = unicode(codecs.BOM_UTF8, 'utf8')
                print '[Notify]: %s' % string.replace(bom, '')
            except:
                pass

    def make_request(self, url, method, payload=None, headers=None):
        """Make an http request. Return the response."""
        self.log('Request URL: %s' % url)
        self.log('Headers: %s' % headers)
        self.log('Payload: %s' % payload)
        try:
            if method == 'get':
                req = self.http_session.get(url, params=payload, headers=headers, allow_redirects=False,timeout=self.timeout)
            elif method == 'json':  # post
                req = self.http_session.post(url, json=payload, headers=headers, allow_redirects=False,timeout=self.timeout)
            else:  # post
                req = self.http_session.post(url, data=payload, headers=headers, allow_redirects=False,timeout=self.timeout)
            req.raise_for_status()
            self.log('Response code: %s' % req.status_code)
            self.log('Response: %s' % req.content)
            if self.use_cookie:
                self.cookie_jar.save(ignore_discard=True, ignore_expires=False)
            return req
        except requests.exceptions.HTTPError as error:
            self.log('An HTTP error occurred: %s' % error)
            raise
        except requests.exceptions.ProxyError:
            self.log('Error connecting to proxy server')
            raise
        except requests.exceptions.ConnectionError as error:
            self.log('Connection Error: - %s' % error.message)
            raise
        except requests.exceptions.RequestException as error:
            self.log('Error: - %s' % error.value)
            raise

    def send(self, message):
        headers     = {'x-ha-access': self.API_PASSWORD, 'content-type': 'application/json'};
        url         = self.BASE_URL + "api/services/tts/google_say";
        if self.MEDIA_PLAYERS:
            players = [x.strip() for x in self.MEDIA_PLAYERS.split(',')]
            print players
            for player in players:
                send_data   = {"entity_id":"media_player."+player,"message":message};
                print send_data
                data        = json.dumps(send_data);
                res         = False
                try:
                    res     = self.make_request(url=url, method="post", payload=data, headers=headers)
                except Exception as e:
                    pass
                if res:
                    try:
                        return res.json();
                    except:
                        return res.content




def test():
    import configure
    conf    = configure.Configure(debug=True);
    CONFIG  = conf.getConfig();
    print CONFIG
    notify = Notify(config=CONFIG, debug=True);
    notify.send("Testing connection for Pi Doorbell Notifications");


if __name__ == '__main__':
    test();