import functools
import http.server
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

FIXTURE = Path(__file__).parent / "fixture"

# `1.0` is an old version, and is missing the `extra` page, to exercise the switcher's fallback.
VERSIONS = {
    "versions": [
        {"ref": "latest", "label": "2.0 (latest)"},
        {"ref": "1.0", "label": "1.0"},
    ]
}
STAGING = {"staging": True, "live_url": "/profiles/test/latest/en/"}

LANGUAGES = ("en", "es")

# The sidebar, which holds the banner and the switchers, is off-screen at narrow widths.
VIEWPORT = {"width": 1600, "height": 1200}


def build(destination, *, language="en", **environ):
    subprocess.run(
        [
            "sphinx-build",
            "-nW",
            "--keep-going",
            "-q",
            "-b",
            "dirhtml",
            "-D",
            f"language={language}",
            str(FIXTURE),
            str(destination),
        ],
        check=True,
        env=os.environ | environ,
    )


@pytest.fixture(scope="session")
def site(tmp_path_factory):
    """Build the fixture into the directory layout that the documentation is deployed in."""
    root = tmp_path_factory.mktemp("site")

    current = root / "profiles/test/latest"
    for language in LANGUAGES:
        build(current / language, language=language)

    # An old version, which the version switcher offers, and which is missing a page.
    shutil.copytree(current, root / "profiles/test/1.0")
    for language in LANGUAGES:
        shutil.rmtree(root / "profiles/test/1.0" / language / "extra")
    # A staging copy, whose directory is named after the branch that was pushed.
    shutil.copytree(current, root / "staging/profiles/test/some-branch")
    # A root with no versions.json, to exercise degrading when it is unreachable.
    shutil.copytree(current, root / "profiles/unconfigured/latest")

    (root / "profiles/test/versions.json").write_text(json.dumps(VERSIONS))
    (root / "staging/profiles/test/versions.json").write_text(json.dumps(STAGING))

    return root


@pytest.fixture(scope="session")
def server(site):
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(site)
    )
    httpd = http.server.ThreadingHTTPServer(("localhost", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    yield f"http://localhost:{httpd.server_port}"

    httpd.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        yield browser

        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page(viewport=VIEWPORT)

    yield page

    page.close()


@pytest.fixture
def page_without_javascript(browser):
    context = browser.new_context(viewport=VIEWPORT, java_script_enabled=False)

    yield context.new_page()

    context.close()
