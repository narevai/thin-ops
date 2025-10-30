# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-30

### Added
- Data export pipeline with destination management
- Edit dialog for modifying entries
- Dynamic filtering on the cost dashboard

### Fixed
- Removed Dockerfile layer caching

### Dependencies
- Updated `@eslint/js` from 9.29.0 to 9.32.0
- Updated `sonner` from 2.0.5 to 2.0.6
- Updated `@vitejs/plugin-react-swc` from 3.10.2 to 3.11.0
- Updated GitHub Actions: `actions/download-artifact` from v4 to v5
- Updated GitHub Actions: `actions/checkout` from v4 to v5

## [0.1.1] - 2025-07-28

### Security
- Fixed `form-data` vulnerability (unsafe random function in boundary generation)
- Fixed `@eslint/plugin-kit` vulnerability (Regular Expression Denial of Service)

### Fixed
- Disabled ESLint warnings for functions defined inside React components
- Removed redundant dependency to prevent refresh loops
- Configured Dependabot to ignore Python 3.13 updates, keeping project on Python 3.12 (#19) for stability

### Dependencies
- Updated `vite` from 7.0.2 to 7.0.6
- Updated `prettier-plugin-tailwindcss` from 0.6.13 to 0.6.14
- Updated `actions/stale` workflow from v5 to v9 for improved GitHub Actions performance

## [0.1.0] - 2025-07-25

### Added

- **Complete analytics platform**: Full analytics API with 20+ FOCUS use cases endpoints and dashboard with comprehensive charts
- **Multi-cloud provider support**: Azure, AWS, GCP and OpenAI provider integration with multiple authentication methods
- **FOCUS 1.2 compliance**: Updated data pipeline and mappers to FOCUS 1.2 standard
- **Data export capabilities**: CSV and Excel export functionality
- **Demo mode**: Complete demo mode for testing and demonstrations
- **Frontend provider management**: UI for adding and managing cloud providers
- **Hamilton orchestration**: Integrated Hamilton for ETL pipeline management
- **OpenAPI specification**: Complete API documentation
- **Development infrastructure**: Dev containers, enhanced CI/CD, and comprehensive ETL tests
