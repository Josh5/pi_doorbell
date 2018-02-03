import os
import re
import sys
import fnmatch
import json


print sys.version_info
if not sys.version_info[:2] == (2, 7):
    print("This module version requires Python 2.7.")
    sys.exit(1)

from setuptools import setup, find_packages

import versioninfo

module_name = versioninfo.name()
module_version = versioninfo.version()
module_description = versioninfo.description()
module_author = versioninfo.author()
module_email = versioninfo.email()
module_url = versioninfo.url()
module_classifiers = [
    versioninfo.dev_status(),
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Operating System :: Android',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Topic :: Home Automation'
]

print("Building module version %s." % module_version)


def setup_extra_options():
    module_options = {};
    # Get all requirements:
    try:
        import pkg_resources;
    except ImportError:
        pass;
    else:
        f = open("requirements.txt", "r");
        try:
            deps = [str(req) for req in pkg_resources.parse_requirements(f)];
        finally:
            f.close();
        module_options['install_requires'] = deps;
    # List all packages:
    module_options['packages'] = find_packages('.', exclude=['examples*', 'test*']);
    # Setup cli scripts:
    module_options['entry_points'] = {
        'console_scripts': [
            '%s=%s.service:main' % (module_name,module_name)
        ]
    };
    return module_options;


setup(
    name=module_name,
    version=module_version,
    author=module_author,
    author_email=module_email,
    maintainer=module_author,
    maintainer_email=module_email,
    url=module_url,
    description=module_description,
    classifiers=module_classifiers,

    **setup_extra_options()
)
