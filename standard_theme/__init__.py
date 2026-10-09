"""

From Sphinx ReadTheDocs theme.

From https://github.com/ryan-roemer/sphinx-bootstrap-theme.

"""

import os


def get_html_theme_path():
    """Return list of HTML theme paths."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def add_js_files(app):
    """Register switchers.js, so that Sphinx appends a checksum to its URL."""
    if app.config.html_theme == "standard_theme":
        app.add_js_file("js/switchers.js", defer="defer")


def setup(app):
    """Register the theme and its message catalogs, via the ``sphinx.html_themes`` entry point."""
    directory = os.path.abspath(os.path.dirname(__file__))

    app.add_html_theme("standard_theme", directory)
    app.add_message_catalog("sphinx", os.path.join(directory, "locale"))
    # The entry point loads this extension into every build, whatever its theme.
    app.connect("builder-inited", add_js_files)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
