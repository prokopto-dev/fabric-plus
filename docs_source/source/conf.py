import os
import sys
from typing import Any
sys.path.insert(0, os.path.abspath('../..'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FabricPlus'
copyright = '2024, Courtney Caldwell'
author = 'Courtney Caldwell'
release = '0.1'
html_logo = '_static/logo.png'
html_baseurl = 'https://fabricplus.prokopto.dev/'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

# Autodoc settings
autodoc_default_options: dict[str, Any] = {
    "members": True,
    "special-members": True,
}

templates_path: list[str] = ['_templates']
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
