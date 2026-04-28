# Changelog

All notable changes to `detour` will be documented in this file.

The format is based on Keep a Changelog, and this project uses semantic
versioning once releases are tagged.

## [0.1.3] - 2026-04-28

### Added

- Contributing, security, support, and code-of-conduct docs.
- GitHub issue templates for bug reports and feature requests.
- Project URLs, author metadata, and package keywords/classifiers.

## [0.1.2] - 2026-04-28

### Added

- `pothole` command and structured event type for marking obstacles without
  changing the active stack.
- Branch-aware pytest coverage checks in CI and release verification.

## [0.1.1] - 2026-04-28

### Added

- Configurable daily note filename formats.
- LogSeq note style for writing Detour entries under an outline-shaped
  `- Detours` journal block.

## [0.1.0] - 2026-04-28

### Added

- Initial Typer CLI with `start`, `into`, `done`, `back`, `status`, `log`,
  `reset`, and `config` commands.
- Agent-friendly JSON output for core commands.
- Structured `event` command for machine-authored transitions.
- Optional idempotency keys for `start` and `into`.
- `started_at` metadata in stack state.
- JSON stack state under the platform state directory.
- Daily Markdown note appends with automatic `## Detours` section creation.
- TOML config support and test-friendly environment overrides.
- AGPL-3.0-only license.
- CI, lint, type-check, package-build, and audit checks.
