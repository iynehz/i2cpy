# Changelog

## [0.2.1] - 2025-07-20

### Changed

- Make ch347 error message explicit when no ACK is received from device.

## [0.2.0] - 2025-07-13

### Added

- ch347 driver support.

### Changed

- Dropped Python 3.8 support. This library now requires Python >=3.9.

### Fixed

- Linux: ch341 with QingHeng's official driver version 1.5, although scan() is
  still broken.


## [0.1.6] - 2025-04-09

### Fixed

- Fix py38 compatibility.
- Doc: Explicitly say macOS is not supported.


## [0.1.5] - 2025-02-25

### Fixed

- Fix multi-device support on Linux. ([GH 2](https://github.com/iynehz/i2cpy/issues/2))

## [0.1.4] - 2025-02-15

### Fixed

- Fix readfrom_mem() when addrsize is not 8. ([GH 1](https://github.com/iynehz/i2cpy/issues/1))

## [0.1.3] - 2024-09-30

### Fixed

- Fix Python version badge in README.

## [0.1.2] - 2024-09-30

### Added

- Doc: Better structured installation instructions.
- Doc: Examples how to write your own wrapper functions to have an "int" interface. 

### Fixed

- Fix Python 3.8 compatibility. And minimally requires Python 3.8.

## [0.1.1] - 2024-06-01

### Fixed

- Fix package metadata.

## [0.1.0] - 2024-05-22

### Added

- First stable release.


[unreleased]: https://github.com/iynehz/i2cpy/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/iynehz/i2cpy/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/iynehz/i2cpy/compare/v0.1.6...v0.2.0
[0.1.6]: https://github.com/iynehz/i2cpy/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/iynehz/i2cpy/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/iynehz/i2cpy/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/iynehz/i2cpy/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/iynehz/i2cpy/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/iynehz/i2cpy/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/iynehz/i2cpy/releases/tag/v0.1.0
