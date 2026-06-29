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

## 2026-06-29 Unified Baseline

### Completed this round

- Unified local workspace, GitHub `main`, and server repository checkout to one public baseline.
- Promoted the public baseline to commit `aeb77dd`.
- Removed the private audit handoff document from the tracked repository.
- Added this shared continuous development document for cross-team collaboration.
- Replaced the repository document path drift with a public `MarkItDown`-based document collection path.
- Restored public executable APIs for:
  - `collect_web`
  - `collect_video`
  - `collect_article`
  - `collect_document`
  - `collect_book`
  - `generate_note`
  - `create_note`
  - `search_notes`
- Moved reusable KMM operational scripts into the repository:
  - `book_cache_manager.py`
  - `book_keyword_index.py`
  - `book_to_skill.py`
  - `doc_parse_router.py`
  - `gbrain_compact.py`
  - `gbrain_link_orphans.py`
  - `gray_validation_suite.py`
  - `knowledge_discovery.py`
  - `knowledge_fetch_router.py`
  - `lightweight_recall.py`
  - `nightly_maintenance.py`
  - `onedrive_bidirectional_sync.sh`
  - `recall_shadow_compare.py`
  - `sensenova_dispatcher.py`
- Removed hard-coded business defaults from public code, including default gbrain page slug lists.
- Switched the server repository remote away from a tokenized GitHub URL to a clean public URL.

### Validation completed

- Local KMM tests: `32 passed`
- GitHub working copy tests: `32 passed`
- `python -m compileall src scripts tests`: passed
- Sensitive-string scan completed for:
  - server IP
  - server absolute paths
  - previous business slugs
  - old version marker `0.0.2`

## Planning Assessment

### What the project has now achieved

KMM now meets the minimum bar for a shared public development baseline:

- one synchronized repository state across local, GitHub, and server checkout
- public KMM runtime code in-repo rather than only in server-side private paths
- executable public APIs backed by tests
- configurable host integration through `AGENT_HOME` and `HERMES_HOME` fallbacks
- collaboration documentation for follow-on contributors

### What the project has not fully achieved yet

KMM still does **not** fully meet the broader planning target of being a fully mature, independently installable, operationally closed-loop knowledge platform.

The main remaining gaps are:

1. The server **production runtime** is still not fully replaced by the repository install output.
2. Some optional adapters and docs still assume Hermes-style environments more strongly than an agent-agnostic design would prefer.
3. Public docs still partially describe a larger operating model than the repository alone guarantees end to end.
4. Observability, deployment, rollback, and gray-release workflows are not yet fully productized inside KMM itself.

### Current judgement

- Public repository maturity: medium
- Server production parity: partial
- Multi-agent portability: partial
- Planning completion: not complete

## Remaining Work Required

To meet the original planning direction more fully, the project still needs:

1. **Repository-to-runtime closure**
   The repository installer must become the actual source of truth for the KMM runtime used on the server.

2. **Production cutover**
   KMM-related scripts in the server agent script directory should be replaced, one by one, with versions deployed from this repository, with rollback notes and verification.

3. **Stronger agent-agnostic cleanup**
   Keep `AGENT_HOME` as the primary contract and reduce host-specific assumptions in docs, defaults, and helper scripts.

4. **Public documentation tightening**
   README should describe only what this repository can actually install and run.

5. **Operational validation**
   Add repeatable smoke tests for:
   - fresh install
   - upgrade
   - uninstall safety
   - sync behavior
   - recall behavior

## Recommended Next Directions

### Priority 1

- Replace the server-side KMM runtime scripts with repository-managed installed scripts.
- Validate that the repository installer produces the same usable KMM runtime behavior.

### Priority 2

- Split public KMM capabilities from private server-only operational workflows more explicitly.
- Keep business automation, channel publishing, and unrelated server operations out of KMM.

### Priority 3

- Strengthen document ingestion:
  - batch processing
  - fallback routing
  - OCR-aware conversion strategy
  - better structured metadata

### Priority 4

- Strengthen retrieval quality:
  - fused ranking across note/state/gbrain/Hindsight layers
  - configurable scoring
  - better deduplication
  - clearer result provenance

### Priority 5

- Strengthen book workflows:
  - richer keyword index lifecycle
  - cache/download/analysis handoff
  - structured recommendation surfaces

### Priority 6

- Strengthen release engineering:
  - CI for KMM tests and sensitive scans
  - release checklist
  - gray rollout checklist
  - rollback procedure

## Next-Step Working Plan

The next preferred implementation sequence is:

1. audit the current KMM-related scripts under the server agent script directory
2. map each one to:
   - already covered by repository
   - needs repository enhancement
   - should remain outside KMM
3. cut over covered scripts to repository-installed versions
4. verify server behavior through gray validation
5. only then continue feature expansion

## 2026-06-29 Runtime Closure Follow-up

### Additional work completed

- Added repository-managed script inventory:
  - `configs/managed_scripts.txt`
- Added public release and rollout assets:
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/GRAY_ROLLOUT.md`
  - `docs/ROLLBACK.md`
  - `docs/SERVER_SCRIPT_MAPPING.md`
- Added CI workflow:
  - `.github/workflows/ci.yml`
- Added repository-sensitive scan:
  - `scripts/sensitive_scan.py`
- Updated installer to read managed scripts from a manifest file.
- Updated installer to record a lightweight install manifest in the target scripts directory.
- Updated uninstall behavior to clean up the managed KMM script set more consistently.
- Fixed installed-script import resolution so runtime scripts prefer:
  - `KMM_PLUGIN_DIR`
  - `AGENT_HOME/knowledge-plugin`
  - repository `src/`
- Performed server-side repository-based KMM install into the server agent home directory.
- Ran server-side validation successfully:
  - `verify_plugin.sh`
  - `gray_validation_suite.py`

### Server validation result

Repository-managed KMM scripts can now run from the installed server location under the current server environment.

Observed successful validation points:

- import smoke passed
- knowledge discovery script executed
- lightweight recall executed for multiple queries
- sync dry-run was safely skipped because no explicit `KMM_SYNC_REMOTE` was set for the validation invocation
- markitdown became available when installation was directed to the Hermes venv

### Current status against the 1-6 roadmap

1. **Repository-to-runtime closure**
   Partially completed.
   The installer and managed script inventory now exist, and server installation was validated.

2. **Production cutover**
   Partially completed.
   Repository-managed KMM scripts were installed and validated on the server, but the server checkout still contains uncommitted local modifications because the latest local import-fix commit was applied outside the GitHub mainline sync path.

3. **Stronger agent-agnostic cleanup**
   Improved.
   `AGENT_HOME`-first behavior is stronger across runtime scripts, installer docs, and validation helpers.

4. **Public documentation tightening**
   Improved.
   Release, rollout, rollback, and mapping docs now exist, and public docs more closely reflect repository-backed behavior.

5. **Operational validation**
   Improved.
   Sensitive scan, CI workflow, and gray validation support now exist.

6. **Release engineering**
   Improved.
   The repository now includes explicit release and rollout assets.

### Remaining unresolved items

- GitHub `main` is still missing the most recent local import-resolution fix commit if network push remains unavailable.
- The server repository working tree is currently dirty because those import-resolution files were copied into place for runtime validation.
- KMM cron cutover was intentionally not changed in this round because the rollout used `KMM_SKIP_CRON=1` for a safer gray validation.
- Some runtime outputs still surface historical session content that contains private server paths inside recall results; this is coming from existing memory/state data, not from the repository code itself.

### Immediate next actions

1. Push the remaining local fix commit to GitHub when outbound connectivity is available.
2. Fast-forward the server repository checkout to that GitHub commit so the server repo returns to a clean state.
3. Decide whether to let the repository installer take over KMM-managed cron entries in production.
4. If cron cutover is approved, rerun install with:
   - `KMM_SKIP_CRON=0`
   - explicit `KMM_SYNC_REMOTE` if sync should be managed by KMM

## 2026-06-30 Real Usage Verification

### End-to-end smoke added

- Added `scripts/kmm_e2e_smoke.py`

This smoke exercises real KMM behavior rather than only unit-test mocks:

- temporary local web collection via live HTTP server
- article collection in URL mode and keyword mode
- video capture note generation
- document conversion and note generation
- note generation API
- note creation and search API
- recent-note discovery
- book cache index rebuild
- book keyword index build and search
- actual rclone local-remote sync:
  - copy to remote
  - copy from remote
  - bisync
- actual installed script execution:
  - `knowledge_discovery.py`
  - `lightweight_recall.py`
  - `doc_parse_router.py`
  - `book_to_skill.py`

### Local real-usage result

The smoke passed locally in the current machine environment.

### Server real-usage result

The smoke passed on the server when run against:

- installed plugin directory: `/root/.hermes/knowledge-plugin`
- installed script directory: `/root/.hermes/scripts`
- Hermes venv Python
- temporary smoke `AGENT_HOME` to avoid polluting production note/state locations

### Practical conclusion

For the repository-backed KMM public/runtime feature set, the core functions are now:

- implemented
- installed on the server
- actually executed
- verified with real outputs

This does **not** mean every broader ecosystem item ever mentioned in historical docs is fully productized.
It means the repository-backed KMM feature surface itself has now been real-use tested.
