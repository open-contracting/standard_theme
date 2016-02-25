# Open Contracting Standard Sphinx Theme

This is the Sphinx theme used for the Open Contracting Standard documentation. It is a fork of the Read the Docs Sphinx Theme, the original readme for that can be found at [RTD_THEME_README.rst](RTD_THEME_README.rst).

## Set up your environment

The [Set up your environment](https://github.com/open-contracting/standard_theme/blob/open_contracting/RTD_THEME_README.rst#set-up-your-environment) instructions in the original README are for Macs. On a recent version of Ubuntu (e.g. 15.10) you can do:

```
sudo aptitude install nodejs ruby-sass npm
npm config set prefix '~/.npm-packages'
export PATH="$PATH:$HOME/.npm-packages/bin" # and put this line in your ~/.bashrc
# (if running 'node' doesn't bring up a command prompt (>)
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

On older versions (e.g. 14.04) ruby-sass is not recent enough, so you will need to install nodejs and npm only, and do a `gem install sass` instead.

Then, as in the other README:

```
npm install -g bower grunt-cli
npm install
grunt
```

NB: grunt - watches for changes and automatically recompiles.

## How to edit the theme files

By default the branch that is checked out is called `open_contracting` - that's the one used on the live site. Don't mess with master (that's upstream).

So we can work on bug and feature branches, and then merge into the open-contracting branch when happy

So checkout your working branch

Make changes to e.g. sass files (grunt will detect the changes and automatically recompile the files)

To see the changes you have made

run `./build_docs.sh` (in the standard docs root - line 44 of the README.md)
run python server
see the changes, make more changes, build the docs, see changes etc

Once finished with changes:
* stop grunt (with control-C)
* run `grunt build` (TODO: Explain why)
* commit changes to the standard_theme repo


## Translations

The theme uses babel's setup.py integration for translations:

```
# create the pot file
python setup.py extract_messages

# push to transifex
tx push -s

# get from transifex
tx pull 
```
