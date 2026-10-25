import flask_storm

project = "Flask-Storm"
copyright = "2016-2026, Andreas Runfalk"
author = "Andreas Runfalk"

release = flask_storm.__version__
version = ".".join(release.split(".")[:2])

extensions = ["sphinx.ext.autodoc"]
add_module_names = False

html_theme = "alabaster"
pygments_style = "sphinx"
