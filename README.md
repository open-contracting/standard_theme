# Open Contracting Standard Sphinx Theme

This is the Sphinx theme used for the [Open Contracting Standard documentation](https://github.com/open-contracting/standard). It is a fork of the Read the Docs Sphinx Theme, the original readme for that can be found at [RTD_THEME_README.rst](/RTD_THEME_README.rst).

We forked the theme rather than inheriting from it, because Sphinx's Jinja templates only allow one level of overrides. By having our own (forked) theme, we can have one theme for all versions of the standard, but make version-specific overrides on the apprpriate branch.

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

1. Change into the `standard`'s directory
1. Run `pip install -e path` where `path` is the path to the theme's directory
1. Run `make` (or `make source` for English only)
1. Change into the `build` directory
1. Run `python -m http.server`
1. Repeat from "Make changes" until done

Commit changes:

1. Stop `grunt` (Ctrl-C)
1. Run `grunt build`
1. Commit changes

## Translations

The theme uses babel's `setup.py` integration for translations:

Create the pot file:

    python setup.py extract_messages

Push to Transifex:

    tx push -s

Pull from Transifex:

    tx pull
