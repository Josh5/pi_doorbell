import io
import os
import sys
import json

import pi_doorbell.version as version_info

__MODULE_VERSION = None
__MODULE_NAME    = None
__MODULE_AUTHOR  = None
__MODULE_EMAIL   = None
__MODULE_URL     = None
__MODULE_DESC    = None


def name():
    global __MODULE_NAME
    __MODULE_NAME = str(version_info.read_info()["name"])
    return __MODULE_NAME


def version():
    global __MODULE_VERSION
    __MODULE_VERSION = version_info.read_info()["version"]
    return __MODULE_VERSION

def description():
    global __MODULE_DESC
    __MODULE_DESC = str(version_info.read_info()["description"])
    return __MODULE_DESC

def author():
    global __MODULE_AUTHOR
    __MODULE_AUTHOR = str(version_info.read_info()["author"])
    return __MODULE_AUTHOR

def email():
    global __MODULE_EMAIL
    __MODULE_EMAIL = str(version_info.read_info()["email"])
    return __MODULE_EMAIL

def url():
    global __MODULE_URL
    __MODULE_URL = str(version_info.read_info()["website"])
    return __MODULE_URL


def branch_version():
    return version()[:3]


def is_pre_release():
    version_string = version()
    return "a" in version_string or "b" in version_string


def dev_status():
    _version = version()
    if 'a' in _version:
        return 'Development Status :: 3 - Alpha'
    elif 'b' in _version or 'c' in _version:
        return 'Development Status :: 4 - Beta'
    else:
        return 'Development Status :: 5 - Production/Stable'


def changes():
    """Extract part of changelog pertaining to version.
    """
    _version = version()
    with io.open(os.path.join(get_base_dir(), "CHANGES.txt"), 'r', encoding='utf8') as f:
        lines = []
        for line in f:
            if line.startswith('====='):
                if len(lines) > 1:
                    break
            if lines:
                lines.append(line)
            elif line.startswith(_version):
                lines.append(line)
    return ''.join(lines[:-1])


def get_base_dir():
    return os.path.abspath(os.path.dirname(sys.argv[0]))
