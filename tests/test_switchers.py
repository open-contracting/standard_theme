"""
Test the banner and the switchers that switchers.js renders from a versions.json document.

The version switcher navigates asynchronously: it checks whether the page exists in the target version before going
there. The waits below are for that, and for the versions.json request on page load.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from tests.conftest import build

CUSTOM_BANNER = "A banner from the documentation repository."
OLD_BANNER = "This is an old version of the documentation. Go to the latest version: 2.0 (latest)."
STAGING_BANNER = (
    "This is a development copy of the documentation. Go to the live version."
)

VERSION_LABELS = ["Version", "2.0 (latest)", "1.0"]

CURRENT = "/profiles/test/latest/en/"
OLD = "/profiles/test/1.0/en/"
STAGING = "/staging/profiles/test/some-branch/en/"
UNCONFIGURED = "/profiles/unconfigured/latest/en/"


def text(browser, selector):
    """Return the text of the matching element, whether or not it is scrolled into view."""
    return " ".join(
        browser.find_element(By.CSS_SELECTOR, selector)
        .get_attribute("textContent")
        .split()
    )


def visit(browser, server, path):
    browser.get(f"{server}{path}")
    # Wait for the banner to be decided, which is the last thing the versions.json response triggers.
    WebDriverWait(browser, 5).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    return browser


def switch(browser, name, label, server, expected):
    Select(
        browser.find_element(By.XPATH, f"//select[@name='{name}']")
    ).select_by_visible_text(label)
    WebDriverWait(browser, 10).until(
        expected_conditions.url_to_be(f"{server}{expected}")
    )


@pytest.mark.parametrize(
    ("path", "expected"), [(CURRENT, ""), (OLD, OLD_BANNER), (STAGING, STAGING_BANNER)]
)
def test_banner(browser, server, path, expected):
    visit(browser, server, path)

    WebDriverWait(browser, 5).until(lambda d: text(d, ".oc-banner") == expected)


@pytest.mark.parametrize(("path", "href"), [(OLD, CURRENT), (STAGING, CURRENT)])
def test_banner_link(browser, server, path, href):
    visit(browser, server, path)

    link = WebDriverWait(browser, 5).until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".oc-banner a")
    )
    assert link.get_attribute("href") == f"{server}{href}"


# A documentation repository adds its own banner by overriding the block, so it isn't conditional on versions.json.
@pytest.mark.parametrize("path", [CURRENT, OLD, STAGING, UNCONFIGURED])
def test_custom_banner(browser, server, path):
    visit(browser, server, path)

    assert text(browser, ".oc-custom-banner") == CUSTOM_BANNER


def test_version_options(browser, server):
    visit(browser, server, CURRENT)

    select = WebDriverWait(browser, 5).until(
        lambda d: Select(d.find_element(By.XPATH, "//select[@name='branch']"))
    )
    WebDriverWait(browser, 5).until(
        lambda d: len(select.options) == len(VERSION_LABELS)
    )
    assert [
        option.get_attribute("textContent") for option in select.options
    ] == VERSION_LABELS


# A staging copy lists no versions, because its directories are named after the branch that was pushed.
@pytest.mark.parametrize("path", [STAGING, UNCONFIGURED])
def test_version_switcher_hidden(browser, server, path):
    visit(browser, server, path)

    assert not browser.find_element(
        By.CSS_SELECTOR, ".oc-version-switcher"
    ).is_displayed()


def test_version_switcher(browser, server):
    visit(browser, server, f"{CURRENT}guidance/")

    switch(browser, "branch", "1.0", server, f"{OLD}guidance/")


# `extra` is missing from the old version, so the switcher falls back to its home page.
def test_version_switcher_falls_back(browser, server):
    visit(browser, server, f"{CURRENT}extra/")

    switch(browser, "branch", "1.0", server, OLD)


def test_language_switcher(browser, server):
    visit(browser, server, f"{CURRENT}guidance/")

    switch(browser, "lang", "Español", server, "/profiles/test/latest/es/guidance/")


# The shape that tests/test_common.py in standard_profile_template asserts.
def test_language_switcher_from_home_page(browser, server):
    visit(browser, server, CURRENT)

    switch(browser, "lang", "Español", server, "/profiles/test/latest/es/")


# Without JavaScript there is no banner and no version switcher, and the language switcher falls back to links.
def test_degrades_without_javascript(browser_without_javascript, server):
    browser = browser_without_javascript
    browser.get(f"{server}{OLD}")

    assert text(browser, ".oc-banner") == ""
    assert text(browser, ".oc-custom-banner") == CUSTOM_BANNER
    assert not browser.find_element(
        By.CSS_SELECTOR, ".oc-version-switcher"
    ).is_displayed()


# The links are relative, so they need no server: this is what replaces posting to `{root}/{version}/switcher`.
@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (CURRENT, ["/profiles/test/latest/en/", "/profiles/test/latest/es/"]),
        (
            f"{CURRENT}guidance/",
            [
                "/profiles/test/latest/en/guidance/",
                "/profiles/test/latest/es/guidance/",
            ],
        ),
        (OLD, ["/profiles/test/1.0/en/", "/profiles/test/1.0/es/"]),
    ],
)
def test_language_links_without_javascript(
    browser_without_javascript, server, path, expected
):
    browser = browser_without_javascript
    browser.get(f"{server}{path}")

    links = browser.find_elements(By.CSS_SELECTOR, ".oc-language-link")
    assert [link.get_attribute("href") for link in links] == [
        f"{server}{url}" for url in expected
    ]


def test_language_link_navigates_without_javascript(browser_without_javascript, server):
    browser = browser_without_javascript
    browser.get(f"{server}{CURRENT}guidance/")

    [
        link
        for link in browser.find_elements(By.CSS_SELECTOR, ".oc-language-link")
        if link.text == "Español"
    ][0].click()

    assert browser.current_url == f"{server}/profiles/test/latest/es/guidance/"


def test_no_server_side_includes(site):
    assert (
        "<!--#include" not in (site / "profiles/test/latest/en/index.html").read_text()
    )


# Until a documentation repository sets versions_url, the theme must emit the server-side includes that Apache
# resolves, unchanged.
def test_server_side_include_without_versions_url(tmp_path):
    build(tmp_path, FIXTURE_VERSIONS_URL="")

    assert '<!--#include virtual="$BANNER" -->' in (tmp_path / "index.html").read_text()
