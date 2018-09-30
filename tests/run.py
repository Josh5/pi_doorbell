#!/usr/bin/python3

import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.path.insert(0, "../pi_doorbell")
    import pi_doorbell
    service = pi_doorbell.Service()
    service.run();