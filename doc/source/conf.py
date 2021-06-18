# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

# -*- coding: utf-8 -*-
#
# cf_units documentation build configuration file, created by
# sphinx-quickstart on Thu Jan 21 12:03:35 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os

import cf_units


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'cf-units'
copyright = 'Copyright cf-units contributors'


current_version = cf_units.__version__
version = current_version.split('+')[0]
release = current_version


# -- Options for HTML output ----------------------------------------------

html_theme = 'alabaster'

html_static_path = ['_static']


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
