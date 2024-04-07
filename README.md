# sherpa
[![CI sherpa](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml)

A simple CLI tool for loading GIS files to a PostGIS database.

`sherpa` aims to be a simpler alternative to GDAL's [ogr2ogr](https://gdal.org/programs/ogr2ogr.html), focusing purely
on loading data to a PostGIS instance.

## Installation

It is recommended to install `sherpa` in a Python virtual environment so there's no dependency conflicts.

Installation requires an up-to-date version of `pip`:
```shell
pip install -U pip
```

For a regular, non-development install:
```shell
pip install git+https://github.com/kyoh-dev/sherpa.git#egg=sherpa
```

## Usage

```
$ sherpa

 Usage: sherpa [OPTIONS] COMMAND [ARGS]...

 A CLI tool for loading GIS files to a PostGIS database

╭─ Commands ──────────────────────────────────────────────────────────╮
│ dsn                Manage your DSN profile                          │
│ load               Load a file to a PostGIS table                   │
│ tables             Get info about tables in your PostGIS instance   │
╰─────────────────────────────────────────────────────────────────────╯
```
