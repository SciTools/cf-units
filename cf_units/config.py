# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.


import configparser
import os.path
import sys


# Returns simple string options.
def get_option(section, option, default=None):
    """
    Returns the option value for the given section, or the default value
    if the section/option is not present.

    """
    value = default
    if config.has_option(section, option):
        value = config.get(section, option)
    return value


# Figure out the full path to the "cf_units" package.
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# The full path to the configuration directory of the active cf_units instance.
CONFIG_PATH = os.path.join(ROOT_PATH, "etc")

# Load the optional "site.cfg" file if it exists.
if sys.version_info >= (3, 2):
    config = configparser.ConfigParser()
else:
    config = configparser.SafeConfigParser()
config.read([os.path.join(CONFIG_PATH, "site.cfg")])
