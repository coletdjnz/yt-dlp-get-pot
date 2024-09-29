# Changelog

## [Unreleased]

## [0.2.0]

### Changed

- Productionize after upstream PO Token support merged. Minimum yt-dlp version is `2024.09.27`

## [0.1.1]

### Fixed

- Logger warning `once` parameter not being passed down correctly (by [grqz](https://github.com/grqz))

## [0.1.0]

### Added

- New `VERSION` attribute to GetPOTProvider. Shown in verbose output for debugging purposes.
- A changelog

### Changed

- Improve logging output
- Re-raise `NoSupportingHandlers` error raised within a Provider as a `RequestError`

[unreleased]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.0.3...v0.1.0