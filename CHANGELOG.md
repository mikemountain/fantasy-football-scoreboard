# Changelog

All notable changes to this project will hopefully be documented in this file.
Expect maximum jank until 0.1.0, minimum. We're talking WD-40 and duct tape code.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres as best as I can bother to try 
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.4] -2020-09-11

### Added

### Changed
- readme
- scores are now getting pulled from different source, updates slower but actually works now so who cares?
- efficient score checking (only checks during game times on thur/sun/mon, can improve this later too)

### Removed
- all the draft stuff now because there's no point now

### Fixed
- technically everything because it didn't actually work before, and now it does. More specifically, I fixed getting the score

## [0.0.3] - 2020-09-09

### Added
- will display the team name instead of username if it's available and fits

### Changed
- readme
- if the week is 0, we'll move into pre-game of week 1 now (some ugly code there)
- removed the player-download until I do something with it
- countdown stuff got moved to a common function
- little visual tweaks

### Removed
- some of the draft stuff because I didn't get it to finish it in time
- took out --team-id option thing in the args because it wasn't working as I intended, gone til fixed

### Fixed
- countdown didn't count down to actual gametime, now it does

## [0.0.2] - 2020-08-14

### Added
- added a changelog I guess
- general robustness, it was pretty janky (still is)
- added a bit of pre-draft/draft stuff (still jank)
- added countdown to kickoff after draft

### Changed
- readme crap
- made a refresh image function to save space

### Removed

### Fixed
- checks for weeks being negative (pre-season, duh)
- avatars weren't getting downloaded
- hopefully logos dir gets created with proper permissions now
