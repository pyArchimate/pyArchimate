# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyArchimate'
# copyright = ''
author = 'Xavier Mayeur'
version = "1"
release = '1.0.1'

import os
import sys
sys.path.insert(0, os.path.abspath('../src/pyArchimate'))
sys.path.insert(0, os.path.abspath('../src/pyArchimate/readers'))
sys.path.insert(0, os.path.abspath('../src/pyArchimate/writers'))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary'
]

templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

root_doc = 'src'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Customization of the style sheet
html_css_files = [
    'custom.css',
]