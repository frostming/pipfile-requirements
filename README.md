# pipfile-requirements
CLI tool to covert Pipfile/Pipfile.lock to requirments.txt

[![Build Status](https://travis-ci.org/frostming/pipfile-requirements.svg?branch=master)](https://travis-ci.org/frostming/pipfile-requirements)
[![Build status](https://ci.appveyor.com/api/projects/status/gketl2i4mhjt53l5?svg=true)](https://ci.appveyor.com/project/frostming/pipfile-requirements)
[![](https://img.shields.io/pypi/v/pipfile-requirements.svg)](https://pypi.org/project/pipfile-requirements)
[![](https://img.shields.io/pypi/pyversions/pipfile-requirements.svg)](https://pypi.org/project/pipfile-requirements)

## Required Python version

`>=2.7, >=3.4`

## What does it do?

The tool is built on top of [requirementslib](https://github.com/sarugaku/requirementslib) to provide a simple CLI to
convert the Pipenv-managed files to requirements.txt.

Pipenv is a great tool for managing virtualenvs and dependencies, but it may be not that useful in deployment.
Pip installation is much faster than Pipenv manipulation, since the latter needs extra requests to PyPI for hash checking.
Installing a Pipenv in deployment may be overkilled. We just need a requirements.txt to tell CI or production server
which packages and versions should be installed.


## Installation

```bash
$ pip install pipfile-requirements
```

An executable named `pipfile2req` will be ready for use in the bin path.

## Usage:

```
$ pipfile2req --help
usage: pipfile2req [-h] [-p PROJECT] [--hashes] [-d] [file]

positional arguments:
  file                  The file path to covert, support both Pipfile and
                        Pipfile.lock. If it isn't given, will try Pipfile.lock
                        first then Pipfile.

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Specify another project root
  --hashes              whether to include the hashes
  -d, --dev             whether to choose the dev-dependencies section
  -s, --sources         whether to include extra PyPi indexes
```

## License

[MIT](/LICENSE)

## Others

It is my first time to use Poetry to manage my project, related to Pipenv, lol.
