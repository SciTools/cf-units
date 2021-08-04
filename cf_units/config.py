# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.


import configparser
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


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


def get_xml_path():
    """Return the alternative path to the UDUNITS2 XMl file"""
    default = Path(sys.prefix) / "share" / "udunits" / "udunits2.xml"
    path = get_option(
        "System",
        "udunits2_xml_path",
        default=str(default),
    )
    return path.encode()


# Figure out the full path to the "cf_units" package.
ROOT_PATH = Path(__file__).resolve().parent

# The full path to the configuration directory of the active cf_units instance.
CONFIG_PATH = ROOT_PATH / "etc"

# The full path to the configuration file.
SITE_PATH = CONFIG_PATH / "site.cfg"

# Load the optional "site.cfg" file if it exists.
config = configparser.ConfigParser()

# Auto-generate the "site.cfg" only when it doesn't exist
# *and* the UDUNITS2 XML file/s are bundled within the cf-units
# package i.e., typically for a wheel installation.
xml_database = None
if not SITE_PATH.is_file():
    SHARE_PATH = CONFIG_PATH / "share"
    xml_database = SHARE_PATH / "udunits2.xml"
    if not xml_database.is_file():
        xml_database = SHARE_PATH / "udunits2_combined.xml"
        if not xml_database.is_file():
            xml_database = None
    if xml_database is not None:
        with NamedTemporaryFile(mode="w+t", delete=False) as tmp:
            site_cfg = f"""[System]
            udunits2_xml_path = {xml_database}
            """
            tmp.file.write(site_cfg)
        SITE_PATH = Path(tmp.name)

# Only attempt to read and parse an existing "site.cfg"
if SITE_PATH.is_file():
    config.read([SITE_PATH])
    if xml_database is not None:
        # Tidy the auto-generated file.
        SITE_PATH.unlink()
