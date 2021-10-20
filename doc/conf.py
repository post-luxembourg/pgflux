# pylint: skip-file
import pgflux

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
master_doc = "index"
project = "pgflux"
copyright = "2021, Michel Albert"
author = "Michel Albert"
version = pgflux.__version__
release = pgflux.__version__
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
todo_include_todos = False
html_static_path = ["_static"]
htmlhelp_basename = "pgfluxdoc"
latex_elements = {}

latex_documents = [
    (
        "index",
        "pgflux.tex",
        "pgflux Documentation",
        "Michel Albert",
        "manual",
    ),
]
extlinks = {
    "issue": ("https://redmine.ipsw.dt.ept.lu/issues/%s", "#"),
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
