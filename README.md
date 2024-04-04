# sherpa
[![CI sherpa](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml)

A simple CLI tool for loading GIS files to a PostGIS database.

`sherpa` aims to be a simpler alternative to GDAL's [ogr2ogr](https://gdal.org/programs/ogr2ogr.html), focusing purely
on loading data to a PostGIS instance.

## Installation

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
$ sherpa --help

 Usage: sherpa [OPTIONS] COMMAND [ARGS]...

 A CLI tool for loading GIS files to a PostGIS database.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                                         │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation. [default: None]  │
│ --help                                                       Show this message and exit.                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ config                        Get and set configuration options                                                                                                  │
│ load                          Load a file to a PostGIS table                                                                                                     │
│ tables                        List tables in a specified schema (default: public)                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Development

For a development install, clone the repository and install with extra dev/test dependencies:
```shell
git clone https://github.com/kyoh-dev/sherpa.git

cd sherpa

pip install -e '.[dev,test]'
```

### Project goals

- [x] Use DSN(s) through a stored config file
- [x] Support loading a GIS file to a PostGIS instance
- [x] Support listing tables in schema with record counts
- [x] Support table creation on load with schema inference
- [ ] Support specifying CRS transform on load
- [ ] Support truncating a table before loading
- [ ] Support using and managing multiple DSNs
- [ ] Improve load performance
- [ ] Investigate using devcontainers as a replacement for docker-compose
