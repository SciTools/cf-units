# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.

from importlib import metadata

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = "cf-units"
copyright = "Copyright cf-units contributors"

current_version = metadata.version("cf_units")
version = current_version.split("+")[0]
release = current_version

# -- Options for HTML output ----------------------------------------------

html_theme = "alabaster"
html_theme_options = {
    "description": f"version {release}",
}

intersphinx_mapping = {"python": ("http://docs.python.org/3/", None)}
