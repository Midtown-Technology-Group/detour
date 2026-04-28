# Security Policy

## Supported Versions

Security fixes are expected to target the latest tagged release.

## Reporting a Vulnerability

Please report security issues privately to Midtown Technology Group instead of
opening a public GitHub issue.

Email: security@midtowntg.com

Include:

- affected version or commit
- operating system
- reproduction steps
- potential impact
- any relevant logs with secrets removed

We will acknowledge reports when received and coordinate a fix before public
disclosure when appropriate.

## Scope

`detour` is a local CLI. The main security-sensitive surfaces are:

- local state and config files
- Markdown notes written to user-selected paths
- dependency supply chain and release workflow

Do not include secrets, tokens, or customer-sensitive data in issue reports,
test fixtures, screenshots, or generated notes.
