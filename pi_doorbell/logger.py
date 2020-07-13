#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     12 July, 2020 (21:33:00)
#   Last Modified by:         Josh.5 
#                             on 12 July, 2020 (21:33:00)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################


import sys
import logging
root_logger         = logging.getLogger()
pi_doorbell_logger  = logging.getLogger("pi_doorbell")


def get_logger(name=None):
    if name:
        log = logging.getLogger("pi_doorbell." + name)
    else:
        log = pi_doorbell_logger
    return log

def set_log_handler_config(log_level=logging.DEBUG):
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s:%(levelname)s:%(name)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    pi_doorbell_logger.info("Setting log level to: %s" % log_level);


