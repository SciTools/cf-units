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
# Note: `project_copyright` can also be used to avoid Ruff "variable shadowing"
# error; https://github.com/sphinx-doc/sphinx/issues/9845#issuecomment-970391099
copyright = "Copyright cf-units contributors"  # noqa: A001

current_version = metadata.version("cf_units")
version = current_version.split("+")[0]
release = current_version

# -- Options for HTML output ----------------------------------------------

html_theme = "alabaster"
html_theme_options = {
    "description": f"version {release}",
}

intersphinx_mapping = {"python": ("http://docs.python.org/3/", None)}
