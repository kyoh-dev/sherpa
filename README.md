# sherpa

A CLI tool for loading GIS files to a PostGIS database

## Installation

Installation requires an up-to-date version of `pip`:
```shell
pip install -U pip
```

...

## Usage

...

## Development

For a development install, clone the repository and install with extra dev/test dependencies:
```shell
git clone https://github.com/kyoh-dev/sherpa.git

cd sherpa

pip install -e '.[dev,test]'
```

## TODO

### Project goals

- [ ] Manage DSN(s) through a stored config file
- [ ] Support loading a GIS file to a PostGIS instance
- [ ] Support specifying CRS transform on load
- [ ] Support table creation on load
- [ ] Support listing tables in schema with record counts
- [ ] Support truncating a table before loading
