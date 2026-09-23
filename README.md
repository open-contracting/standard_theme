# Open Contracting Standard Sphinx Theme

This is the Sphinx theme used for the [Open Contracting Standard documentation](https://github.com/open-contracting/standard). It is a fork of the Read the Docs Sphinx Theme, the original readme for that can be found at [RTD_THEME_README.rst](/RTD_THEME_README.rst).

We forked the theme rather than inheriting from it, because Sphinx's Jinja templates only allow one level of overrides. By having our own (forked) theme, we can have one theme for all versions of the standard, but make version-specific overrides on the appropriate branch.

## Banners and version switcher

Set the `versions_url` theme option to render the sidebar's banner and version switcher from a `versions.json` document, instead of from Apache's server-side includes.

```python
html_theme_options = {
    # Relative to the version's directory, so that one value serves the live and staging copies.
    "versions_url": "../versions.json",
    # Optional, for a build whose URL has no version directory, like a local build.
    "branch": os.getenv("GITHUB_REF_NAME", ""),
}
```

Serve a `versions.json` at each documentation root (`/`, `/infrastructure/`, `/profiles/ppp/`, …) and at each staging root. Edit it on release: every published page reads it, so no version is rebuilt.

```json
{
  "versions": [
    {"ref": "latest", "label": "1.1.5 (latest)"},
    {"ref": "1.0", "label": "1.0.3"}
  ]
}
```

- `versions` lists the versions the switcher offers, current version first. `ref` is the directory below the documentation root, and `label` is the option's text.
- Omit `versions` to hide the switcher, as a staging copy does: its directories are named after the branch that was pushed.
- Omit a directory that is only an alias, like a `1.1` symlinked to the current version's. The theme shows no banner on an unlisted version, rather than treating it as old.
- `staging` (default `false`) shows the development-copy banner, and `live_url` is that banner's link. Omit `live_url` for no link.

The page's URL decides the banner: the development-copy banner under a `staging` root, the old-version banner where the URL's version directory is listed but isn't the first, and no banner otherwise. Override the `banner` block to add a banner of the repository's own, which renders regardless.

Without `versions_url`, the theme writes `<!--#include virtual="$BANNER" -->` and the `version_options` block, for Apache's `mod_include` to resolve at request time. Without JavaScript, or where `versions.json` is unreachable, the page has no banner and no version switcher.

## Language switcher

Set the `languages` theme option to build the switcher's options, and a `<noscript>` list of relative links to the same page in each language.

```python
html_theme_options = {
    "languages": {"en": "English", "es": "Español"},
}
```

The links need no server, so the form has no `action`. Without the option, the theme uses the `language_options` block, and submits the form to `{root}/{version}/switcher` for Apache to rewrite.

`versions_url` and `languages` are independent. Setting either loads [switchers.js](standard_theme/static/js/switchers.js), which navigates on `change`, checking that the target page exists before leaving the current one.

## Tests

`tests/` builds the Sphinx project in `tests/fixture`, lays it out as the documentation is deployed (`{root}/{version}/{language}/`, with a staging copy and an old version), serves it, and drives Chrome over it.

```shell
uv run --group dev pytest
```

The tests cover what [switchers.js](standard_theme/static/js/switchers.js) decides, which a Sphinx build alone can't show: which banner each deployment state gets, the version switcher's options and its fallback to a version's home page, both switchers navigating to the same page, and the page without JavaScript. One test builds with `versions_url` empty, to hold the server-side includes unchanged for the documentation repositories that haven't migrated.

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
