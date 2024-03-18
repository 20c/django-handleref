# Changelog


## Unreleased
### Fixed
- fix reversional handler to only update version field on HandleRef models (thanks to @ercpe)


## 2.0.0
### Added
- python 3.11 support
- django 4.2 support
### Removed
- python 3.7 support


## 1.1.0
### Added
- python 3.10 support
- django 4.0 support
### Fixed
- issue with pagination in object history view causing timeout (#19)
### Removed
- python 3.6 support
- django 2.2 support


## 1.0.2
### Fixed
- fix list index of range issue in version admin


## 1.0.1
### Fixed
- performance issues in admin version history view


## 1.0.0
### Added
- python 3.9
- Django to current
### Removed
- python2 support
- EOL Django support


## 0.6.0
### Added
- django3.0 support


## 0.5.0
### Added
- django2.2 support


## 0.4.1
### Fixed
- add grappelli templates to MANIFEST.in


## 0.4.0
### Added
- version admin tools: history, revert and rollback


## 0.3.0
### Added
- py3 compatibility


## 0.2.0
### Added
- tox test django 1.8, 1.9, 1.10 and 1.11
- support handle_version in later versions of reversion
### Changed
- when soft-deleting dont re-save already deleted children