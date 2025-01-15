# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-03-14

### Added
- ETF.com integration as primary data source
- Browser automation for reliable data collection
- Rate limiting and caching system
- Multi-source validation for metrics
- Debug logging capabilities
- Automatic fallback mechanisms
- Detailed error reporting
- Chrome/ChromeDriver setup instructions

### Changed
- Improved expense ratio collection with priority sources
- Enhanced error handling for web scraping
- Better data validation and parsing
- Updated documentation with new features

### Fixed
- ETF.com parsing issues
- Expense ratio accuracy
- AUM comparison calculations
- Volume data validation 

## [Unreleased]

### Fixed
- Fixed missing benchmark initialization in ETFAnalyzer class
- Added IIV (Indicative Intraday Value) field to real-time data responses
- Fixed real-time data collection when market is closed
- Updated test mocks to properly handle market closed scenarios
- Fixed validation test failures by adding proper mock data

### Changed
- Updated test suite to use pytest fixtures for consistent mocking
- Improved error handling in real-time data collection
- Enhanced debug logging for better issue tracking

### Added
- New mock_analyzer fixture for consistent test behavior
- Added debug logging to help track data flow
- Added validation for IIV field presence in real-time data

### Technical
- Improved test coverage for ETFAnalyzer class
- Added proper mocking for yfinance API calls
- Fixed divide by zero warnings in tracking error calculations 