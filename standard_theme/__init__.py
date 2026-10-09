"""

From Sphinx ReadTheDocs theme.

From https://github.com/ryan-roemer/sphinx-bootstrap-theme.

"""

import os


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
