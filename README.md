# sherpa
[![CI sherpa](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kyoh-dev/sherpa/actions/workflows/ci.yml)

A simple CLI tool for loading GIS files to a PostGIS database.

`sherpa` aims to be a simpler alternative to GDAL's [ogr2ogr](https://gdal.org/programs/ogr2ogr.html), focusing purely
on loading data to a PostGIS instance.

## Installation

TBC

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

## Development

TBC

### TODO

- [ ] Update docs and tests
- [ ] Fix error handling
  - [ ] Fail loads early when issues occur (i.e. invalid data type)
  - [ ] More descriptive error messages
  - [ ] Add support for list and dict types -> JSONB columns
- [ ] Support specifying CRS transform on load
- [ ] Support truncating a table before loading
- [ ] Support using and managing multiple DSNs
- [ ] Improve load performance
- [ ] Investigate using devcontainers as a replacement for docker-compose
