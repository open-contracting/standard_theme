# Open Contracting Standard Sphinx Theme

This is the Sphinx theme used for the [Open Contracting Standard documentation](https://github.com/open-contracting/standard). It is a fork of the Read the Docs Sphinx Theme, the original readme for that can be found at [RTD_THEME_README.rst](/RTD_THEME_README.rst).

We forked the theme rather than inheriting from it, because Sphinx's Jinja templates only allow one level of overrides. By having our own (forked) theme, we can have one theme for all versions of the standard, but make version-specific overrides on the appropriate branch.

## Banners and version switcher

By default, the theme writes a `<!--#include virtual="$BANNER" -->` server-side include into the sidebar, and each
documentation repository overrides the `version_options` block with another server-side include. Apache's
`mod_include` resolves both at request time.

Setting the `versions_url` theme option replaces both with markup that [switchers.js](standard_theme/static/js/switchers.js)
fills in from a `versions.json` document, so that the documentation renders its own banner and version switcher on any
static host. The two mechanisms are independent: a repository that doesn't set `versions_url` is unaffected.

```python
html_theme_options = {
    # Relative to the version's directory, so that the same value works for the staging and live copies.
    "versions_url": "../versions.json",
    "branch": os.getenv("GITHUB_REF_NAME", ""),
}
```

`versions.json` is a deployment-level artifact, one per documentation root (`/`, `/infrastructure/`, `/profiles/ppp/`,
…) and one per copy (live and staging). Keeping it outside the build is what allows a new release to reach the pages
of every already-built version without rebuilding them.

```json
{
  "versions": [
    {"ref": "latest", "label": "1.1.5 (latest)"},
    {"ref": "1.0", "label": "1.0.3"}
  ]
}
```

- `versions` lists the versions offered by the switcher, current version first. `ref` is the directory below the
  documentation root; `label` is the text of the option. Omit it to hide the switcher, as a staging copy does: its
  directories are named after the branch that was pushed, which no static file can enumerate.
- `staging` (default `false`) switches the banner to the development-copy banner.
- `live_url` is the link in the development-copy banner. Omit it for no link.

A version that is only an alias, such as a `1.1` directory symlinked to the current version's, is left out of
`versions`. The theme then shows no banner there, rather than treating it as an old version.

The banner is the theme's, and the page's URL decides which one to show: the development-copy banner if `staging` is
set, the old-version banner if the URL's version directory is in `versions` but isn't the first one, and no banner
otherwise. A documentation repository can add a banner of its own by overriding the `banner` block.

`branch` is only a fallback, for a build that is served outside the `{root}/{version}/{language}/` directory layout,
such as a local build. It matters because a version can be served from more than one directory: `latest` is a symlink
to the current version's directory, so a page built from the `1.1` branch is old under `/1.0/` but current under
`/latest/`. Only the URL can tell the two apart.

Without JavaScript, or if `versions.json` is unreachable, the page shows no banner and no version switcher, and the
language switcher falls back to submitting its form to `{root}/{version}/switcher`.

## Tests

`tests/` builds the Sphinx project in `tests/fixture`, lays it out as the documentation is deployed
(`{root}/{version}/{language}/`, with a staging copy and an old version), serves it, and drives Chrome over it. Run:

```shell
uv run --group dev pytest
```

The tests cover what [switchers.js](standard_theme/static/js/switchers.js) decides, which a Sphinx build alone can't
show: which banner each deployment state gets, the version switcher's options and its fallback to a version's home
page when a page is missing there, both switchers navigating to the same page, and the page staying usable without
JavaScript. One test builds the fixture with `versions_url` empty, to hold the server-side includes unchanged for
the documentation repositories that haven't migrated.

## Setting up the environment

The [instructions](/RTD_THEME_README.rst#set-up-your-environment) in the original README are for macOS. On a recent version of Ubuntu (like 15.10), you can run:

```
sudo aptitude install nodejs npm ruby-sass
npm config set prefix '~/.npm-packages'
export PATH="$PATH:$HOME/.npm-packages/bin" # and put this line in your ~/.bashrc
# (if running 'node' doesn't bring up a command prompt (>)
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

On older versions (like 14.04), run `gem install sass` instead of installing `ruby-sass` with aptitude.

Then, as in the original README:

```
npm install -g bower grunt-cli
npm install
```

## Editing the theme

Create a working branch:

1. Checkout the `open_contracting` branch (`master` is upstream)
1. Checkout a working branch
1. Run `grunt` to automatically detect changes and recompile CSS files

Make changes:

1. Make changes to SASS files

Preview changes:

1. Change to the `standard`'s directory
1. Run `pip install -e path` where `path` is the path to the theme's directory
1. Run `make` (or `make source` for English only)
1. Run `python -m http.server --directory build`
1. Repeat from "Make changes" until done

Commit changes:

1. Stop `grunt` (Ctrl-C)
1. Run `grunt build`
1. Commit changes

## Translations

```shell
pybabel extract . -F pyproject.toml -o locale/sphinx.pot -k '_ l_ lazy_gettext'
pybabel update -N -i locale/sphinx.pot -d locale -D sphinx
```
