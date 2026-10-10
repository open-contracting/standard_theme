"""Test the navigation that theme.js sets up and the search page that search.js renders."""

import json

import pytest
from playwright.sync_api import expect

CURRENT = "/profiles/test/latest/en/"
GUIDANCE = f"{CURRENT}guidance/"
SEARCH_URL = (
    "https://standard.open-contracting.org/search/ocdsindex_en/_search?size=100"
)


@pytest.mark.parametrize("path", [CURRENT, GUIDANCE, f"{CURRENT}search/?q=example"])
def test_no_javascript_errors(page, server, path):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.route(
        SEARCH_URL,
        lambda route: route.fulfill(json={"hits": {"total": {"value": 0}, "hits": []}}),
    )

    page.goto(f"{server}{path}")
    page.wait_for_load_state("load")

    assert errors == []


def test_tables_are_responsive(page, server):
    page.goto(f"{server}{GUIDANCE}")

    expect(page.locator(".wy-table-responsive > table.docutils")).to_have_count(1)


def test_expand_links(page, server):
    page.goto(f"{server}{GUIDANCE}")

    item = page.locator(".wy-menu-vertical li.toctree-l2").first
    expand = item.locator(":scope > a > .toctree-expand")
    expect(expand).to_have_count(1)
    expect(item).not_to_have_class("toctree-l2 current")

    expand.click()
    expect(item).to_have_class("toctree-l2 current")

    expand.click()
    expect(item).not_to_have_class("toctree-l2 current")


def test_anchor_opens_navigation(page, server):
    page.goto(f"{server}{GUIDANCE}#subsection")

    expect(page.locator(".wy-menu-vertical li.toctree-l3.current")).to_have_count(1)


def test_mobile_menu(page, server):
    page.set_viewport_size({"width": 400, "height": 800})
    page.goto(f"{server}{GUIDANCE}")

    page.locator("[data-toggle='wy-nav-top']").click()
    expect(page.locator("nav.wy-nav-side")).to_have_class("wy-nav-side shift")

    page.locator("[data-toggle='wy-nav-top']").click()
    expect(page.locator("nav.wy-nav-side")).to_have_class("wy-nav-side")


def test_search(page, server):
    requests = []

    def handle(route):
        requests.append(route.request)
        route.fulfill(
            json={
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_source": {
                                "url": f"{server}{GUIDANCE}#section",
                                "title": "<b>Section</b>",
                            },
                            "highlight": {"text": ["An <em>example</em> match"]},
                        }
                    ],
                }
            }
        )

    page.route(SEARCH_URL, handle)
    page.goto(f"{server}{CURRENT}search/?q=example+query")

    expect(page.locator("#results-list li")).to_have_count(1)
    expect(page.locator('#rtd-search-form input[name="q"]')).to_have_value(
        "example query"
    )
    expect(page.locator("#results-count")).to_have_text(
        "Found one page matching the search query."
    )

    link = page.locator("#results-list a")
    expect(link).to_have_text("<b>Section</b>")
    expect(link).to_have_attribute(
        "href", f"{server}{GUIDANCE}?highlight=example%20query#section"
    )
    expect(page.locator("#results-list .context em")).to_have_text("example")

    body = json.loads(requests[0].post_data)
    assert (
        body["query"]["bool"]["must"]["simple_query_string"]["query"] == "example query"
    )
    assert (
        body["query"]["bool"]["filter"]["term"]["base_url"]
        == f"{server}/profiles/test/latest/"
    )
    assert requests[0].headers["authorization"].startswith("Basic ")


def test_search_translated(page, server):
    hit = {"_source": {"url": "", "title": ""}, "highlight": {"text": [""]}}
    page.route(
        SEARCH_URL.replace("ocdsindex_en", "ocdsindex_es"),
        lambda route: route.fulfill(
            json={"hits": {"total": {"value": 2}, "hits": [hit, hit]}}
        ),
    )
    page.goto(f"{server}/profiles/test/latest/es/search/?q=ejemplo")

    expect(page.locator("#results-count")).to_have_text(
        "Se encontraron 2 páginas que coinciden con la consulta de búsqueda."
    )
