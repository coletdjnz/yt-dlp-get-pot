# Changelog

## [Unreleased]

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

[unreleased]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/coletdjnz/yt-dlp-get-pot/compare/v0.0.3...v0.1.0