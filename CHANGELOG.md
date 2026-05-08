# Changelog

Äá»‹nh dáº¡ng changelog nÃ y Ä‘i theo tinh tháº§n Keep a Changelog vÃ  version theo SemVer.

## [Unreleased]

## [0.1.2] - 2026-05-08

### Changed

- Renamed repository and Python distribution to `reclip-holilihu-mcp`.
- Renamed the primary MCP server id to `reclip-holilihu-mcp`.
- Added `reclip-holilihu-mcp` CLI entry point while keeping legacy aliases.
- Updated plugin path and marketplace metadata to `plugins/reclip-holilihu-mcp`.
- Setup scripts now remove the legacy `holilihu-reclip` MCP config block before writing the new config.

## [0.1.1] - 2026-05-08

### Added

- Community health files for contributors, support, security, and issue triage.
- Issue templates and pull request template.
- CI smoke tests for the Flask API, CLI, and MCP server.
- Dependabot configuration with grouped updates.
- OpenSSF Scorecard workflow for scheduled security posture checks.
- Architecture, release, localization, roadmap, and maintainer documentation.

### Changed

- Updated GitHub Actions versions.
- Clarified Vietnamese-first project language status.

## [0.1.0] - 2026-05-08

### Added

- HoLiLiHu ReClip fork from the original ReClip project.
- Bounded concurrent download manager shared by the web app and MCP server.
- Codex MCP tools for video info, one-off downloads, batch downloads, status, runtime checks, and history.
- CLI commands: `setup-mcp`, `print-mcp-config`, `doctor`, `serve`, and `run-mcp`.
- Repo-local Codex plugin scaffold.
- Windows release workflow that builds `HoLiLiHu-ReClip-Setup.exe`.
- MIT attribution notice for the original ReClip project.

[Unreleased]: https://github.com/meiiie/reclip-holilihu-mcp/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/meiiie/reclip-holilihu-mcp/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/meiiie/reclip-holilihu-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/meiiie/reclip-holilihu-mcp/releases/tag/v0.1.0

