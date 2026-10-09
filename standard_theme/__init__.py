"""

From Sphinx ReadTheDocs theme.

From https://github.com/ryan-roemer/sphinx-bootstrap-theme.

"""

import os

from sphinx.util.logging import getLogger

logger = getLogger(__name__)


def get_html_theme_path():
    """Return list of HTML theme paths. Deprecated: setting html_theme_path stops setup() from running."""
    logger.warning(
        "Calling get_html_theme_path is deprecated: remove it and html_theme_path, so that the theme is found "
        "through its entry point. Found by path, it registers neither its scripts nor its message catalogs."
    )
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def add_js_files(app):
    """Register the theme's scripts, so that Sphinx appends a checksum to each URL."""
    # theme.js reads window.jQuery as it loads, and the sticky navigation calls into it, so it must come last.
    if not os.environ.get("READTHEDOCS"):
        app.add_js_file("js/theme.js", priority=800)
    app.add_js_file("js/switchers.js", defer="defer")


def setup(app):
    """Register the theme and its message catalogs, via the ``sphinx.html_themes`` entry point."""
    directory = os.path.abspath(os.path.dirname(__file__))

    app.add_html_theme("standard_theme", directory)
    app.add_message_catalog("sphinx", os.path.join(directory, "locale"))
    app.connect("builder-inited", add_js_files)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
