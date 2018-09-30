#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
#
#   Written by:               Josh.5 (jsunnex@gmail.com)
#   Date:                     21 February, 2017 (11:11:50)
#   Last Modified by:         Josh.5 
#                             on 04 February, 2018 (08:24:42)
#
#   Copyright:
#          Copyright (C) StreamingTech LTD. - All Rights Reserved
#          Unauthorized copying of this file, via any medium is strictly prohibited
#          Proprietary and confidential
#
###################################################################################################

# Dummy file to make this directory a package.

import warnings


from .service import Service

from .version import __author__
from .version import __version__

__all__ = (
    'Service',
)

