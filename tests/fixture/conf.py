import os

import standard_theme

project = "Test"
copyright = "Open Contracting Partnership"

html_theme = "standard_theme"
html_theme_path = [standard_theme.get_html_theme_path()]
templates_path = ["_templates"]

html_theme_options = {
    "root_url": "/profiles/test",
    "short_project": "Test",
    # Empty for the server-side include, which is what a documentation repository that hasn't migrated emits.
    "versions_url": os.getenv("FIXTURE_VERSIONS_URL", "../versions.json"),
    "branch": os.getenv("FIXTURE_BRANCH", ""),
    "languages": {"en": "English", "es": "Español"},
}
