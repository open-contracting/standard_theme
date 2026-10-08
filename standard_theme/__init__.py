"""

From Sphinx ReadTheDocs theme.

From https://github.com/ryan-roemer/sphinx-bootstrap-theme.

"""

import os


def get_html_theme_path():
    """Return list of HTML theme paths."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def setup(app):
    """Register the theme and its message catalogs, via the ``sphinx.html_themes`` entry point."""
    directory = os.path.abspath(os.path.dirname(__file__))

    app.add_html_theme("standard_theme", directory)
    app.add_message_catalog("sphinx", os.path.join(directory, "locale"))

    return {"parallel_read_safe": True, "parallel_write_safe": True}
