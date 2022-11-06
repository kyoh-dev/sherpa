# sherpa

A CLI tool for loading GIS files to a PostGIS database

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

```shell
sherpa --help
                                                                                
    Usage: sherpa [OPTIONS] COMMAND [ARGS]...                                      
                                                                                    
    A CLI tool for loading GIS files to a PostGIS database.
    ╭─ Options ────────────────────────────────────────────────────────────────────╮
    │ --install-completion        [bash|zsh|fish|powershe  Install completion for  │
    │                             ll|pwsh]                 the specified shell.    │
    │                                                      [default: None]         │
    │ --show-completion           [bash|zsh|fish|powershe  Show completion for the │
    │                             ll|pwsh]                 specified shell, to     │
    │                                                      copy it or customize    │
    │                                                      the installation.       │
    │                                                      [default: None]         │
    │ --help                                               Show this message and   │
    │                                                      exit.                   │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────╮
    │ config        Get and set configuration options                              │
    │ info          Get info about your PostGIS tables                             │
    │ load          Load a file to a PostGIS table                                 │
    ╰──────────────────────────────────────────────────────────────────────────────╯

```

## Development

For a development install, clone the repository and install with extra dev/test dependencies:
```shell
git clone https://github.com/kyoh-dev/sherpa.git

cd sherpa

pip install -e '.[dev,test]'
```

## TODO

### Project goals

- [x] Use DSN(s) through a stored config file
- [x] Support loading a GIS file to a PostGIS instance
- [x] Support listing tables in schema with record counts
- [ ] Support specifying CRS transform on load
- [ ] Support table creation on load
- [ ] Support truncating a table before loading
- [ ] Support using and managing multiple DSNs
