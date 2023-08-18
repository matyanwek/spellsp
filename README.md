# SpelLSP

Typical spellcheck features wrapped in a language server.

Supported features:
- dictionary formats:
    - [x] plain
    - [x] Hunspell
    - [ ] Aspell
    - [ ] Vim
- Spell Checking Diagnostics:
    - [x] basic word detection
    - [x] wrong-case
    - [ ] affixes
- [ ] Fix Suggestions
- [ ] Completion Suggestions
- [ ] In-Editor Word Additions
- [ ] Grammar Checking

## Installation

To install, clone the git repository, build the package, and install with pip:
```console
$ git clone https://github.com/matyanwek/spellsp
$ cd spellsp
$ python3 setup.py bdist_wheel
$ pip3 install .
```

The cloned git directory can then be deleted.

To uninstall, use pip then clean the build files:
```console
$ pip3 uninstall spellsp
$ pip3 uninstall -y spellsp
$ cd spellsp
$ rm -r build dist *.egg-info **/*.egg-info
```

## Usage

Set up your editor's LSP settings with the following command line arguments:
- `-d` -- the dictionary file (Hunspell format or a plain text word list)
- `-i` -- the input file handle (defaults to stdin)
- `-o` -- the input file handle (defaults to stdout)
