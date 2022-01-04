# coding=utf-8
import os
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/..")

project = "api"
version = "0.0.1"

html_search_language = "en"
html_show_copyright = False
todo_include_todos = False
add_module_names = False
show_authors = False
html_show_sourcelink = False
html_show_sphinx = False
docs_path = "."
html_theme_options = {}
html_theme = "sphinx_rtd_theme"
master_doc = "index"
source_encoding = "utf-8"
source_suffix = [".rst", ".md"]


pygments_style = "sphinx"
# html_logo = os.path.join(docs_path, "_static/logo.svg")
# html_favicon = os.path.join(docs_path, "_static/favicon.ico")
# templates_path = [os.path.join(docs_path, "_templates")]
# html_static_path = [os.path.join(docs_path, "_static")]
exclude_dirs = []  # do not include in autodoc
nitpicky = False
html_use_index = True
add_function_parentheses = True


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinxcontrib.napoleon",  # requires sphinxcontrib-napoleon
    "m2r2",  # new md -> rst
    "sphinx_click",  # requires sphinx-click
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
