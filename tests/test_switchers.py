"""Test the banner and the switchers that switchers.js renders from a versions.json document."""

import pytest
from playwright.sync_api import expect

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


def hrefs(page, selector):
    """Return the links' resolved URLs, rather than their relative href attributes."""
    return page.locator(selector).evaluate_all("links => links.map(link => link.href)")


@pytest.mark.parametrize(
    ("path", "expected"), [(CURRENT, ""), (OLD, OLD_BANNER), (STAGING, STAGING_BANNER)]
)
def test_banner(page, server, path, expected):
    page.goto(f"{server}{path}")

    expect(page.locator(".oc-banner")).to_have_text(expected)


@pytest.mark.parametrize(("path", "href"), [(OLD, CURRENT), (STAGING, CURRENT)])
def test_banner_link(page, server, path, href):
    page.goto(f"{server}{path}")
    expect(page.locator(".oc-banner a")).to_be_attached()

    # The old-version banner builds an absolute URL; the staging banner uses `live_url` as written.
    assert hrefs(page, ".oc-banner a") == [f"{server}{href}"]


# A documentation repository adds its own banner by overriding the block, so it isn't conditional on versions.json.
@pytest.mark.parametrize("path", [CURRENT, OLD, STAGING, UNCONFIGURED])
def test_custom_banner(page, server, path):
    page.goto(f"{server}{path}")

    expect(page.locator(".oc-custom-banner")).to_have_text(CUSTOM_BANNER)


def test_version_options(page, server):
    page.goto(f"{server}{CURRENT}")

    expect(page.locator("select[name=branch] option")).to_have_text(VERSION_LABELS)


# A staging copy lists no versions, because its directories are named after the branch that was pushed.
@pytest.mark.parametrize("path", [STAGING, UNCONFIGURED])
def test_version_switcher_hidden(page, server, path):
    page.goto(f"{server}{path}")

    expect(page.locator(".oc-version-switcher")).to_be_hidden()


def test_version_switcher(page, server):
    page.goto(f"{server}{CURRENT}guidance/")
    expect(page.locator(".oc-version-switcher")).to_be_visible()

    page.select_option("select[name=branch]", label="1.0")

    page.wait_for_url(f"{server}{OLD}guidance/")


# `extra` is missing from the old version, so the switcher falls back to its home page.
def test_version_switcher_falls_back(page, server):
    page.goto(f"{server}{CURRENT}extra/")
    expect(page.locator(".oc-version-switcher")).to_be_visible()

    page.select_option("select[name=branch]", label="1.0")

    page.wait_for_url(f"{server}{OLD}")


def test_language_switcher(page, server):
    page.goto(f"{server}{CURRENT}guidance/")

    page.select_option("select[name=lang]", label="Español")

    page.wait_for_url(f"{server}/profiles/test/latest/es/guidance/")


# The shape that tests/test_common.py in standard_profile_template asserts.
def test_language_switcher_from_home_page(page, server):
    page.goto(f"{server}{CURRENT}")

    page.select_option("select[name=lang]", label="Español")

    page.wait_for_url(f"{server}/profiles/test/latest/es/")


# Without JavaScript there is no banner and no version switcher, and the language switcher falls back to links.
def test_degrades_without_javascript(page_without_javascript, server):
    page = page_without_javascript
    page.goto(f"{server}{OLD}")

    expect(page.locator(".oc-banner")).to_have_text("")
    expect(page.locator(".oc-custom-banner")).to_have_text(CUSTOM_BANNER)
    expect(page.locator(".oc-version-switcher")).to_be_hidden()


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
    page_without_javascript, server, path, expected
):
    page = page_without_javascript
    page.goto(f"{server}{path}")

    assert hrefs(page, ".oc-language-link") == [f"{server}{url}" for url in expected]


def test_language_link_navigates_without_javascript(page_without_javascript, server):
    page = page_without_javascript
    page.goto(f"{server}{CURRENT}guidance/")

    page.click(".oc-language-link:text('Español')")

    page.wait_for_url(f"{server}/profiles/test/latest/es/guidance/")


def test_no_server_side_includes(site):
    assert (
        "<!--#include" not in (site / "profiles/test/latest/en/index.html").read_text()
    )


# Until a documentation repository sets versions_url, the theme must emit the server-side includes that Apache
# resolves, unchanged.
def test_server_side_include_without_versions_url(tmp_path):
    build(tmp_path, FIXTURE_VERSIONS_URL="")

    assert '<!--#include virtual="$BANNER" -->' in (tmp_path / "index.html").read_text()
