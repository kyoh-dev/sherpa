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

### Short-term goals

- [ ] Add info command and sub-commands to get table information
- [ ] Support specifying CRS transform on load
- [ ] Support table creation on load
- [ ] Support listing tables from multiple schemas
- [ ] Option to truncate table before loading

### Long-term goals

- [ ] Support loading to SpatiaLite
- [ ] Support reading and loading different layers of a file
