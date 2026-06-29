# KMM Continuous Development

Last updated: 2026-06-29
Scope: local workspace, GitHub public repository, server repository checkout

## Goal

Keep `Knowledge-and-Memory-Management` as a publishable KMM repository that:

- exposes only reusable KMM code and docs
- avoids server-specific paths, credentials, private audit notes, and user data
- stays aligned across local, GitHub, and server checkout
- remains compatible with `hermes-memory-installer` through stable note and script boundaries

## Baseline

The current unified baseline is:

- feature scope bounded to KMM only
- public runtime implemented in this repository
- optional integration with memory sidecar through `AGENT_HOME`, `HERMES_HOME`, note directories, `gbrain`, and `Hindsight`
- no dependency on server-specific absolute paths or production-only business slugs

## Responsibility Boundary

`hermes-memory-installer` owns:

- session and fact memory runtime
- governance and recall layers
- indexing curated markdown notes into agent recall

KMM owns:

- knowledge collection from web, video, article, document, and book sources
- structured note generation
- note search, discovery, and sync helpers
- optional adapters that call memory-sidecar-compatible tools

## Release Rules

Before pushing changes:

1. Verify no private paths or production notes remain in tracked files.
2. Run repository tests relevant to KMM.
3. Run a targeted sensitive-string scan.
4. Sync the same tree to GitHub and the server checkout.

Do not commit:

- production audit notes
- server-specific absolute paths
- hard-coded business or personal page slugs
- credentials, tokens, cookies, private endpoints, or user data
- generated caches such as `__pycache__` and `.pytest_cache`

## Working Agreement

When adding functionality:

1. Prefer public, configurable implementations first.
2. Use environment variables for host-specific behavior.
3. Keep README claims matched to code that is actually present in this repository.
4. Add or update tests when public APIs or install behavior changes.

When pulling from a server runtime:

1. Copy only KMM-relevant code.
2. Replace host-specific paths with config-driven resolution.
3. Remove business defaults and operational leftovers.
4. Re-run tests before sync.

## Key Paths

- source code: `src/`
- operational helpers: `scripts/`
- tests: `tests/`
- public docs: `docs/`

## Sync Checklist

- local workspace updated
- GitHub repository updated
- server checkout updated
- server-only operational leftovers reviewed separately before reuse
