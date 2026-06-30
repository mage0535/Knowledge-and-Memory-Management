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

- installed plugin directory: the server agent plugin directory
- installed script directory: the server agent script directory
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

## Next Expansion Roadmap

### Guiding principle

The next stage should not prioritize "more sources first".
It should prioritize:

1. higher-quality ingestion
2. higher-quality retrieval
3. more stable orchestration
4. clearer publication and collaboration boundaries

### P0: strengthen document ingestion

Current public KMM already has:

- `MarkItDown`
- `doc_parse_router.py`
- `book_to_skill.py`

The next upgrade should be a multi-engine routing layer with explicit quality fallback:

- `MarkItDown` for lightweight common documents
- `Docling` for layout-aware rich documents
- `MinerU` for OCR-heavy and scanned documents

Recommended open-source integrations:

- [docling-project/docling](https://github.com/docling-project/docling)
- [docling-project/docling-mcp](https://github.com/docling-project/docling-mcp)
- [opendatalab/MinerU](https://github.com/opendatalab/mineru)

Recommended implementation direction:

- upgrade `doc_parse_router.py` into a scored router
- add extraction quality metadata
- add cache reuse by file hash
- persist engine choice and fallback reason

### P1: strengthen web extraction

Current public KMM already has:

- `collect_web`
- `knowledge_fetch_router.py`

Recommended open-source integrations:

- [unclecode/crawl4AI](https://github.com/unclecode/crawl4AI)
- [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)

Recommended implementation direction:

- add source-type classification
- add page quality scoring
- add sitemap / same-domain batch crawl mode
- add dedup fingerprinting before note generation
- add retry / dead-letter handling for failed extraction targets

### P2: strengthen retrieval quality

Current public KMM retrieval works, but ranking quality is still basic.

Recommended open-source integrations:

- [qdrant/qdrant](https://github.com/qdrant/qdrant)
- [qdrant/qdrant-client](https://github.com/qdrant/qdrant-client)
- Jina AI reranker ecosystem (for final-stage rerank)

Recommended implementation direction:

- move from plain layer merge to:
  - query rewrite
  - hybrid retrieval
  - rerank
  - provenance scoring
- store source, layer, retrieval score, rerank score, and final order reason

### P3: strengthen scheduling and observability

Current KMM has runnable cron-oriented scripts, but not yet a full production task control layer.

Recommended open-source integrations:

- [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect)
- [dagu-org/dagu](https://github.com/dagu-org/dagu)

Recommended implementation direction:

- move critical KMM tasks into managed workflows:
  - `knowledge_discovery.py`
  - `nightly_maintenance.py`
  - `book_cache_manager.py`
  - `onedrive_bidirectional_sync.sh`
- add:
  - retries
  - timeout policy
  - last-success markers
  - dead-letter queue
  - health artifacts

### P4: strengthen knowledge publishing and team collaboration

Recommended open-source integrations:

- [outline/outline](https://github.com/outline/outline)

Recommended implementation direction:

- keep KMM as ingestion / refinement / retrieval
- use a separate collaboration-facing knowledge UI for team publishing
- preserve Markdown and note-index boundaries instead of tightly coupling UI and ingestion

## Video Knowledge Extraction Research

### Target platforms

- YouTube
- Bilibili
- TikTok
- Douyin

### Practical extraction principle

Useful video notes should not depend on a single modality.
For these platforms, the stable path is:

1. metadata
2. subtitles / transcript
3. audio transcription fallback
4. scene/keyframe extraction
5. OCR on keyframes and burned-in subtitles
6. timeline-aligned note synthesis

### Recommended open-source components

#### Download / metadata / subtitles

- [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
  Recommended as the default fetch layer for YouTube, Bilibili, TikTok, and many Douyin-accessible flows.

#### YouTube transcript-first path

- [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
  Recommended when YouTube transcripts are available directly and subtitles should be fetched before running ASR.

#### Speech transcription fallback

- [openai/whisper](https://github.com/openai/whisper)
  Recommended as the default multilingual ASR fallback when platform subtitles are missing or low quality.

#### Scene segmentation / keyframe extraction

- [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect)
  Recommended for extracting representative scene boundaries and reducing redundant frames.

#### OCR for frames and burned-in subtitles

- [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
  Recommended for overlay text, burned-in subtitles, and slide-like frames.

Optional practical reference:

- [devmaxxing/videocr-PaddleOCR](https://github.com/devmaxxing/videocr-PaddleOCR)

### Recommended KMM video pipeline

The KMM video note pipeline should be:

```text
URL
  -> platform adapter
  -> metadata fetch
  -> subtitle fetch
  -> if subtitles missing: audio extract + Whisper
  -> scene detect
  -> keyframe select
  -> OCR on keyframes
  -> transcript + OCR + metadata fuse
  -> timeline chunking
  -> note generation
  -> image + text combined note
```

### How to produce readable mixed-media notes

The note format should not be a raw transcript dump.
It should become a structured visual note:

1. cover summary
   - title
   - source platform
   - author / uploader
   - publish time
   - duration
   - key topics

2. executive summary
   - what the video is about
   - why it matters
   - target audience

3. timeline sections
   - timestamp range
   - summary paragraph
   - selected keyframe
   - OCR text extracted from that frame
   - extracted claims / facts / methods

4. key takeaways
   - main points
   - reusable methods
   - notable examples

5. follow-up links
   - related notes
   - related gbrain nodes
   - source URL

### Platform-specific recommendations

#### YouTube

- prefer transcript API or official subtitles first
- fall back to Whisper only when needed
- use scene detection to avoid too many frames

#### Bilibili

- prefer subtitle extraction if present
- capture danmaku/comment context only as optional enrichment, not as primary knowledge

#### TikTok / Douyin

- treat burned-in captions and overlay text as first-class content
- OCR quality matters more than on YouTube long-form video
- use shorter timeline windows and denser frame sampling because visual overlays change rapidly

### Stability considerations

For short-video platforms especially:

- do not assume stable subtitle APIs
- always support audio transcription fallback
- always support OCR fallback
- store adapter diagnostics for failed runs
- keep downloader, transcript, OCR, and summarizer as separate stages for retryability

### Recommended near-term implementation order for video

1. unify metadata + subtitle extraction behind `yt-dlp`
2. add transcript-first / Whisper-fallback logic
3. add `PySceneDetect` keyframe pipeline
4. add `PaddleOCR` frame OCR stage
5. generate timeline-based mixed-media notes
6. only then add platform-specific enrichments such as comments or danmaku

## Anti-Crawl Channel Research

### Scope

This section covers content-heavy platforms where direct extraction is often fragile due to dynamic rendering, request controls, account walls, or anti-automation defenses:

- Xiaohongshu
- WeChat Official Account articles
- Reddit
- Hacker News / similar community feeds
- CSDN

The recommended KMM direction is:

- prefer public or user-authorized access paths
- separate fetching, normalization, media extraction, OCR, translation, and note generation
- avoid tightly coupling KMM to any one brittle scraping trick

### General extraction strategy for defended channels

The stable KMM pattern should be:

```text
URL or user-authorized source
  -> source adapter
  -> metadata extraction
  -> structured content extraction
  -> media capture
  -> OCR / transcript if needed
  -> normalization to Markdown blocks
  -> translation to target audience language
  -> image + text note generation
```

For harder channels, KMM should support three tiers:

1. official/public interfaces first
2. browser-assisted user-authorized extraction second
3. OCR/media fallback last

### Xiaohongshu / RedNote

Practical reality:

- a large amount of useful content is image-first
- many posts depend on app/web rendering details
- OCR is often as important as HTML extraction

Useful open-source references:

- [ReaJason/xhs](https://github.com/ReaJason/xhs)
- [zhjiang22/openclaw-xhs](https://github.com/zhjiang22/openclaw-xhs)
- [bnchiang96/xiaohongshu-importer](https://github.com/bnchiang96/xiaohongshu-importer)
- [kohoj/skills](https://github.com/kohoj/skills)
  Relevant skill reference: Xiaohongshu image posts to Markdown via OCR

Recommended KMM integration direction:

- support user-authorized browser/session capture
- download post media and covers
- OCR image carousels
- preserve note metadata:
  - author
  - topic/tags
  - publish time
  - engagement metrics when available
- generate mixed-media notes where each image becomes:
  - image block
  - OCR text block
  - summary block

### WeChat Official Account articles

Practical reality:

- article pages are often server-rendered and relatively extractable
- fragility mainly comes from request restrictions and occasional verification flows
- article quality is usually text-first, but inline images and embedded video still matter

Useful open-source references:

- [jackwener/wechat-article-to-markdown](https://github.com/jackwener/wechat-article-to-markdown)
- [rrrrrredy/wechat-reader](https://github.com/rrrrrredy/wechat-reader)
- [jj-cheng25/weixin-articles-mcp](https://github.com/jj-cheng25/weixin-articles-mcp)
- [didilili/MagicMD](https://github.com/didilili/MagicMD)

Recommended KMM integration direction:

- prefer article URL -> Markdown normalization
- preserve:
  - title
  - author
  - publish date
  - original source URL
- capture inline images as note assets rather than plain links
- if an article includes video, extract video cover and key frames as auxiliary note blocks

### Reddit

Practical reality:

- HTML pages are not the best source for stable extraction
- thread structure is often easier to recover from JSON-like or API-oriented paths

Useful open-source references:

- [socius-org/RedditHarbor](https://github.com/socius-org/RedditHarbor)
- [datavorous/yars](https://github.com/datavorous/yars)
- [praw-dev/asyncpraw](https://github.com/praw-dev/asyncpraw)
- [NFeruch/reddit2text](https://github.com/NFeruch/reddit2text)

Recommended KMM integration direction:

- prefer structured thread extraction over raw rendered HTML
- capture:
  - post title
  - subreddit
  - post body
  - top comments
  - comment hierarchy summary
- convert long threads into:
  - thread summary
  - key viewpoints
  - representative comments
  - related links/media

### Hacker News / similar community feeds

Practical reality:

- HN is comparatively easy because the official API is public and stable
- value comes less from scraping and more from comment/thread structuring

Useful open-source references:

- [HackerNews/API](https://github.com/HackerNews/API)

Recommended KMM integration direction:

- use the official API rather than page scraping
- capture:
  - story metadata
  - outbound link
  - score
  - comment tree
- generate:
  - story summary
  - key discussion themes
  - notable technical takeaways

### CSDN

Practical reality:

- article pages are often easier to normalize than social feeds
- the main value is high-quality article-to-Markdown conversion plus image preservation

Useful open-source references:

- [didilili/MagicMD](https://github.com/didilili/MagicMD)
- [Aas-ee/open-webSearch](https://github.com/Aas-ee/open-webSearch)
  Reference point for dedicated article fetch tooling

Recommended KMM integration direction:

- treat CSDN similarly to a document/article source
- normalize article body to Markdown
- preserve code blocks, headings, images, and references
- optionally classify article topic automatically into the KMM note taxonomy

## Translation and Audience-Language Rendering

KMM should support note generation in the audience's preferred platform language rather than preserving only source language.

Recommended note-generation pipeline:

1. extract source content blocks
2. classify source language
3. translate summary and explanatory sections into target language
4. preserve original quotations where useful
5. keep OCR text and transcript snippets traceable to the source

Recommended note structure for translated multi-platform content:

- source metadata
- translated executive summary
- original-language excerpt blocks
- image/keyframe blocks
- OCR/transcript blocks
- translated explanation blocks
- key takeaways
- glossary of platform-specific terms

### Practical rendering rule

For high readability, each note block should answer one of:

- what was shown
- what was said
- why it matters
- what should be remembered

### Recommended implementation order for defended-channel ingestion

1. WeChat article normalization
2. Xiaohongshu image-first OCR note pipeline
3. Reddit structured thread ingestion
4. HN official API adapter
5. CSDN article-to-Markdown adapter
6. target-language translation layer for all of the above

## Existing Capability Integration Rule

### Core requirement

KMM already contains multiple partially overlapping capabilities:

- anti-crawl and browser-assisted fetching
- OCR
- video/audio understanding
- document parsing
- note generation
- retrieval
- cloud sync

The next development stage must not treat these as isolated features.
They should be made compatible through one shared ingestion and note-production architecture.

### Compatibility objective

Every supported source should be normalized into the same internal pipeline:

```text
source adapter
  -> content acquisition
  -> media extraction
  -> OCR / ASR / transcript
  -> normalization
  -> translation
  -> note synthesis
  -> retrieval/indexing
  -> sync/publication
```

### Shared integration contract

All ingestion paths should emit a common structured payload with at least:

- `source_type`
- `source_platform`
- `source_url`
- `title`
- `author`
- `published_at`
- `language`
- `content_blocks`
- `image_assets`
- `audio_assets`
- `timeline_blocks`
- `ocr_blocks`
- `transcript_blocks`
- `extraction_quality`
- `fallback_chain`

This common payload is what should feed `generate_note`, retrieval, graph linking, and sync.

### Existing capability mapping

#### 1. Acquisition layer

Use current or planned capabilities here:

- `knowledge_fetch_router.py`
- `collect_web`
- browser-assisted / anti-crawl fetch layer
- `yt-dlp`
- channel-specific adapters for WeChat, Xiaohongshu, Reddit, CSDN, Bilibili, TikTok, Douyin

Goal:

- fetch source content without yet deciding final note format

#### 2. Media understanding layer

Use current or planned capabilities here:

- `Whisper` / `faster-whisper` / `FunASR`
- `PaddleOCR`
- `PySceneDetect`
- document parsing engines:
  - `MarkItDown`
  - `Docling`
  - `MinerU`

Goal:

- turn raw media into usable text, structure, timeline, and visual evidence

#### 3. Normalization layer

This layer should convert heterogeneous channel outputs into one KMM-internal schema.

Examples:

- article body -> section blocks
- forum thread -> post + representative comments
- video -> timeline chunks + keyframes + OCR/transcript blocks
- image-first post -> ordered image blocks + OCR summaries
- document -> section tree + extracted assets

This layer is the key to compatibility.
Without it, KMM remains a loose tool bundle instead of a coherent system.

#### 4. Translation layer

Translation should happen after normalization and before final note rendering.

Rules:

- preserve original-language quotes when useful
- translate summaries, explanations, and labels to the target audience language
- keep OCR/transcript provenance
- never lose source-language traceability

#### 5. Note synthesis layer

The note layer should support three canonical outputs:

1. article-style notes
2. timeline-style media notes
3. image-sequence notes

All of them should reuse:

- source metadata
- structured summaries
- evidence blocks
- image assets
- related-note links

#### 6. Retrieval/indexing layer

After synthesis, all notes should feed the same retrieval surface:

- local markdown search
- state-backed FTS
- optional Hindsight
- optional gbrain
- optional future vector/rerank layer

This avoids building source-specific retrieval silos.

#### 7. Sync/publication layer

After indexing:

- sync through `cloud_sync`
- optionally publish to a collaboration-facing knowledge surface
- keep sync and publishing downstream of note generation, not embedded inside extractors

## Integration Constraints For Existing Features

### Anti-crawl features

Anti-crawl capability should only live in the acquisition layer.
It should not leak into note generation or retrieval code.

What this means:

- browser/session tooling fetches content
- extracted content is handed off as normalized payload
- later stages should not care whether the source required anti-crawl handling

### OCR features

OCR should be usable across:

- short-video overlays
- image-first social posts
- scanned PDFs
- slides and screenshots

This means OCR outputs should be stored as reusable blocks, not hidden inside platform-specific adapters.

### Video recognition features

Video understanding should be decomposed into:

- transcript
- scene segmentation
- keyframe extraction
- frame OCR
- timeline chunk summary

This decomposition is what allows the same note renderer to work for:

- YouTube long-form video
- Bilibili tutorials
- TikTok / Douyin short clips

### Document parsing features

Document engines should compete only inside the parsing layer.
They should not create separate downstream note formats.

That means:

- `MarkItDown`, `Docling`, and `MinerU` should all emit comparable normalized structures
- downstream note synthesis should be engine-agnostic

## Recommended Unified Pipeline Families

### Family A: text-first sources

Applies to:

- WeChat
- CSDN
- most web articles
- Hacker News article links

Pipeline:

```text
fetch
  -> markdown/body extraction
  -> image capture
  -> optional translation
  -> article-style note
```

### Family B: thread/community sources

Applies to:

- Reddit
- Hacker News discussions
- future forum-like sources

Pipeline:

```text
fetch structured thread
  -> flatten hierarchy
  -> extract key viewpoints
  -> quote representative comments
  -> generate discussion-style note
```

### Family C: video-first sources

Applies to:

- YouTube
- Bilibili
- TikTok
- Douyin

Pipeline:

```text
metadata/subtitles
  -> ASR fallback
  -> scene split
  -> keyframe OCR
  -> timeline chunking
  -> mixed-media note
```

### Family D: image-first social sources

Applies to:

- Xiaohongshu
- future screenshot-heavy channels

Pipeline:

```text
image sequence fetch
  -> OCR per image
  -> caption extraction
  -> image ordering
  -> translated explanation
  -> image-sequence note
```

## Immediate integration work recommended

The most important next engineering task is not adding new features.
It is defining and implementing the shared normalized payload and making current features emit it.

Recommended order:

1. define normalized KMM content schema
2. update current web/article/video/document paths to emit that schema
3. make note synthesis consume the schema
4. add translation stage
5. only then add more source adapters

## External Memory Sidecar Integration Confirmation

### Confirmed integration boundary

KMM can already interoperate with the external memory sidecar project through stable filesystem and runtime boundaries.

The confirmed boundary is:

- `AGENT_HOME`
- `HERMES_HOME`
- `AGENT_HOME/knowledge/notes`
- installed helper scripts under `AGENT_HOME/scripts`
- optional access to:
  - `gbrain`
  - `Hindsight`
  - `state.db`

### Confirmed KMM-side behavior

Current KMM behavior already supports sidecar-compatible integration because:

- note generation resolves note storage through `AGENT_HOME` / `HERMES_HOME`
- retrieval scripts can see:
  - local notes
  - state-backed FTS
  - optional Hindsight
  - optional gbrain
- installed scripts are deployable into the same agent home used by the sidecar runtime

### Confirmed sidecar-side behavior

The memory sidecar repository explicitly treats KMM as the upstream knowledge curation layer and indexes curated markdown notes from the agent home knowledge directory.

Confirmed sidecar expectations:

- KMM notes live under `AGENT_HOME/knowledge/notes`
- those notes are indexed into the sidecar knowledge layer
- knowledge notes participate in fused recall alongside session search, Hindsight, and gbrain

### Confirmed evidence

Evidence from `hermes-memory-installer`:

- README states that curated markdown knowledge under `AGENT_HOME/knowledge/notes` participates in recall
- architecture docs describe KMM as the upstream knowledge curation layer
- `tests/test_kmm_integration.py` verifies knowledge-note indexing and retrieval behavior

Evidence from current server environment:

- the server agent home contains:
  - knowledge root
  - notes directory
  - installed KMM plugin directory
  - installed KMM script directory
- these locations were used in repository-based KMM installation and validation

### Agent recognition and calling status

At the current stage, agent recognition and calling are effective through the shared runtime environment rather than through a bespoke direct protocol.

What is already effective:

- the sidecar can recognize KMM note outputs because they are placed in the expected knowledge directory
- KMM scripts can call optional sidecar-adjacent dependencies such as `gbrain` and `Hindsight` when present
- installed KMM scripts are callable from the agent script directory

What is not yet fully formalized:

- a dedicated typed KMM-to-sidecar API contract
- automatic capability discovery between KMM and the sidecar beyond shared path conventions and installed scripts
- a shared normalized knowledge-object protocol between KMM extraction and sidecar governance/indexing

### Practical conclusion

KMM and the external memory sidecar are already data-linked and operationally compatible.
The integration is real and usable today.

However, the current integration style is still:

- path-based
- script-based
- environment-variable-driven

It is not yet a fully formalized contract-first integration.

### Recommended next integration step

The best next step is to define a formal shared contract for:

- note metadata
- extracted knowledge objects
- source provenance
- quality scores
- graph-link hints

Once that contract exists, both:

- KMM extraction pipelines
- sidecar indexing / recall pipelines

can evolve independently without drifting.

## Additional Open-Source Knowledge Capture and Note-System References

Beyond the earlier source-specific extraction tools, the following projects are useful references for the broader KMM + sidecar roadmap.

### AI note and capture systems

- [codexu/note-gen](https://github.com/codexu/note-gen)
  Useful reference for "capture first, organize later" workflows where raw inputs become structured markdown knowledge.

- [usememos/memos](https://github.com/usememos/memos)
  Useful reference for lightweight capture flows, fast note entry, and self-hosted markdown-native note systems.

- [siyuan-note/siyuan](https://github.com/siyuan-note/siyuan)
  Useful reference for privacy-first local knowledge bases, graph-style note linking, and richer PKM surfaces.

- [reorproject/reor](https://github.com/reorproject/reor)
  Useful reference for local semantic note linking, AI note search, and local-first note understanding.

- [lfnovo/open-notebook](https://github.com/lfnovo/open-notebook)
  Useful NotebookLM-style reference for multi-source reading, note synthesis, and research-oriented note presentation.

### Agent-facing second-brain references

- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
  Strong reference for plain-markdown second-brain workflows and AI-assisted note graph building.

- [agenticnotetaking/arscontexta](https://github.com/agenticnotetaking/arscontexta)
  Useful reference for agent-oriented knowledge systems and how context pipelines can be generated around note structures.

- [taurran/pokevault](https://github.com/taurran/pokevault)
  Useful reference for provenance-aware markdown knowledge vaults and portable second-brain patterns.

### Knowledge architecture / research workflow references

- [QZhang2111/Research-Pilot](https://github.com/QZhang2111/Research-Pilot)
  Useful reference for research workflows organized around claims, evidence, experiments, and updates.

- [Trilium Notes](https://github.com/Trilium-Notes)
  Useful reference for hierarchical and scriptable knowledge-base structures with rich organization patterns.

### How these should influence KMM

These projects are not all drop-in dependencies.
Most are stronger as references for:

- capture UX
- note structuring
- provenance tracking
- semantic linking
- research workflow organization
- agent-facing knowledge surfaces

### Practical recommendation

KMM should continue to stay focused on:

- ingestion
- knowledge analysis
- note rendering
- sync
- retrieval preparation

while borrowing from the projects above for:

- note template design
- local-first knowledge UX
- knowledge graph organization
- research workflow structure
- provenance and cross-note linking

## Joint Next-Step Recommendations To Reach Design Goals

To move KMM and the sidecar closer to the full design target, the next expansion and optimization directions should be:

### 1. Shared protocol first

Create and version a shared KMM-sidecar knowledge protocol.

This should define:

- normalized source payload
- extracted knowledge objects
- rendered note outputs
- retrieval/index metadata
- graph-link hints

### 2. Knowledge analysis layer in KMM

Add a dedicated internal layer for:

- fact extraction
- method extraction
- concept extraction
- evidence grouping
- reusable pattern identification

This layer should sit between acquisition and note rendering.

### 3. Knowledge-object indexing in the sidecar

Extend sidecar governance/indexing so that it can index not only rendered markdown notes, but also:

- facts
- concepts
- methods
- references
- provenance anchors

### 4. Retrieval improvement

Add:

- query rewriting
- hybrid retrieval
- reranking
- provenance-aware scoring
- graph-assisted retrieval when available

### 5. Better note rendering system

Turn note output into a small set of canonical renderers:

- article note
- thread note
- timeline media note
- image-sequence note
- reference note

### 6. Better observability across both systems

Add compatible health artifacts for:

- ingestion success/failure
- note generation success/failure
- sync freshness
- retrieval quality signals
- governance freshness
- graph/index freshness

### 7. More explicit agent capability discovery

Move from implicit script/path discovery toward:

- capability manifest
- typed tool descriptors
- optional MCP exposure for KMM workflows

## Overall conclusion

The combined KMM + sidecar system is already functionally useful.
What it now needs most is not raw feature count, but:

- stronger shared contracts
- better knowledge modeling
- better retrieval quality
- better operational clarity

Those changes will make the system easier to extend than simply adding many more source adapters.

## Joint KMM + Sidecar Design-Gap Scan

### Scan conclusion

The current KMM + external memory sidecar combination already works as a real system, but it is still operating as two coordinated subsystems rather than one fully contract-driven platform.

The combined design target is:

- KMM as the upstream knowledge acquisition and refinement layer
- the sidecar as the downstream memory governance and recall runtime
- agents consuming one coherent knowledge and memory surface

This target is only partially complete today.

### What is already strong

#### KMM strengths

- source ingestion and note production now exist as real runnable public code
- note outputs can be generated and synced
- web, article, document, video, and book paths are all present in the repository-backed runtime
- real-use smoke coverage now exists

#### Sidecar strengths

- strong session/memory runtime model
- governance rebuild and tiered recall architecture
- explicit knowledge layer indexing for curated notes
- observability and operations focus

### Main gaps still remaining

#### 1. Shared knowledge-object contract is missing

KMM currently produces notes.
The sidecar currently indexes notes.
What is still missing is a formal intermediate object model shared by both sides.

That model should include:

- note metadata
- extracted entities
- extracted facts
- methods / patterns
- source provenance
- timeline blocks
- quality scores
- graph-link hints

Without this, KMM and the sidecar are compatible, but still loosely coupled.

#### 2. KMM note synthesis is stronger than its knowledge modeling

KMM can create readable notes, but it still needs a clearer distinction between:

- raw extracted content
- structured knowledge objects
- rendered user notes

That separation will make sidecar indexing and future GraphRAG integration much cleaner.

#### 3. Sidecar knowledge indexing is markdown-oriented, not object-oriented

The sidecar already indexes curated notes, which is good.
But the next step should be richer indexing of:

- facts
- concepts
- references
- method cards
- timeline evidence

instead of treating the rendered markdown note as the only primary unit.

#### 4. Retrieval is usable but not yet best-in-class

The current combined system can retrieve:

- local notes
- session search
- Hindsight
- gbrain

But it still lacks:

- query rewriting
- reranking
- source confidence scoring
- knowledge-object-level retrieval
- stronger cross-layer provenance

#### 5. Agent capability discovery is still implicit

Today the agent finds KMM mostly through:

- installed scripts
- shared directory layout
- environment variables

The next maturity step is explicit discoverability:

- capability manifest
- stable tool contract
- optional MCP-style exposure for KMM-specific workflows

## Recommended Next Joint Roadmap

### Priority A: define the shared knowledge contract

This is the single highest-value next step.

Add a formal shared schema between KMM and the sidecar for:

- source asset
- normalized content block
- knowledge object
- rendered note
- graph link hint
- retrieval metadata

This should be versioned and stored in-repo.

### Priority B: split KMM into three internal layers

KMM should be made more explicit internally:

1. acquisition
2. knowledge analysis
3. note rendering

That will make it much easier for the sidecar to consume KMM outputs at the right abstraction level.

### Priority C: upgrade sidecar knowledge indexing

The sidecar should evolve from:

- indexing markdown notes only

to:

- indexing markdown notes
- indexing extracted knowledge objects
- indexing structured provenance

This is where KMM and sidecar become much more than filesystem neighbors.

### Priority D: improve retrieval with hybrid + rerank

Recommended next improvements:

- lexical retrieval
- vector retrieval
- graph retrieval
- rerank
- source-aware final ranking

### Priority E: formalize observability across both systems

KMM and the sidecar should emit compatible health artifacts, including:

- last success
- processed source counts
- extraction quality
- note generation counts
- retrieval hit distribution
- sync state
- graph/index freshness

## Open-Source Projects Worth Borrowing From

These are not all direct dependencies.
Some are better used as design references than as drop-in integrations.

### Knowledge extraction / schema / reasoning

- [google/langextract](https://github.com/google/langextract)
  Strong reference for structured extraction from unstructured content.

### Graph-aware memory / temporal knowledge

- [getzep/graphiti](https://github.com/getzep/graphiti)
  Strong reference for temporally-aware graph memory and provenance.

- [microsoft/graphrag](https://github.com/microsoft/graphrag)
  Strong reference for text-to-graph extraction and graph-aware retrieval design.

- [DEEP-PolyU/Awesome-GraphRAG](https://github.com/DEEP-PolyU/Awesome-GraphRAG)
  Useful survey/reference list for choosing the right GraphRAG patterns.

### Production retrieval orchestration

- [deepset-ai/haystack](https://github.com/deepset-ai/haystack)
  Strong reference for modular retrieval/generation pipelines.

- [deepset-ai/haystack-core-integrations](https://github.com/deepset-ai/haystack-core-integrations)
  Useful integration reference layer.

### External memory references

- [mem0ai/mem0](https://github.com/mem0ai/mem0)
  Useful comparison point for memory-layer abstraction, though KMM + sidecar should keep their own clearer source/refinement boundary.

### Notebook-like knowledge presentation

- open NotebookLM-style projects already listed earlier in this document remain useful references for note presentation and cross-source reading UX.

## Practical recommendation

If only one major architecture task is chosen next, it should be:

**define and implement the shared KMM-sidecar knowledge-object protocol**

That one change would unlock:

- better knowledge extraction
- better indexing
- better retrieval
- cleaner agent calling
- easier future integration with graph and rerank systems

## 2026-06-30 Knowledge Analysis Layer Implementation

### What landed

KMM now has a real public Knowledge Analysis Layer in `src/knowledge_collector/analysis.py`.

The layer implements the first version of the shared knowledge-object protocol:

- schema version: `kmm.knowledge_object.v1`
- normalized content blocks
- source type and source reference
- detected language
- summary
- keywords
- concepts
- claims with evidence snippets
- action items
- open questions
- risks and gaps
- timeline hints
- extraction quality metrics
- metadata for downstream indexing

This is deterministic and dependency-light by design.
It works in local development, CI, public GitHub installs, and server runtime without requiring LLM credentials.

### How it is called

Python API:

```python
from knowledge_collector import analyze_material, generate_note

knowledge = analyze_material(
    {
        "title": "Layered Recall",
        "content": "Layered recall is a memory architecture. It should preserve provenance.",
        "source_ref": "memory://example",
    },
    source_type="note",
)

note = generate_note(
    {
        "title": "Layered Recall",
        "content": "Layered recall is a memory architecture. It should preserve provenance.",
    },
    template="note",
)
```

CLI:

```bash
python3 scripts/knowledge_analysis.py ./source.md
python3 scripts/knowledge_analysis.py --text "KMM should extract useful claims." --title "KMM"
python3 scripts/knowledge_analysis.py ./source.md --markdown
```

### Storage behavior

Every `generate_note(...)` call now writes two artifacts:

- rendered Markdown note: `<note-id>.md`
- machine-readable knowledge object: `<note-id>.knowledge.json`

The Markdown frontmatter contains a `metadata.knowledge_object` pointer with:

- schema version
- object id
- JSON path
- quality metrics
- keywords

This gives the memory sidecar and future GraphRAG indexing a stable object to consume without scraping rendered Markdown.

### Compatibility

Existing public APIs remain compatible:

- `collect_web`
- `collect_article`
- `collect_video`
- `collect_document`
- `collect_book`
- `generate_note`
- `create_note`
- `search_notes`

Collectors still return the same `CollectionResult` fields.
The note generation return payload now includes additional fields:

- `knowledge_path`
- `analysis`

Existing callers that only use `note_id`, `note_path`, `domain`, or `title` continue to work.

### Validation completed locally

The implementation is covered by:

- direct analysis schema tests
- generated-note sidecar JSON tests
- structured Markdown rendering tests
- collector integration tests
- managed script deployment tests
- CLI test for `scripts/knowledge_analysis.py`

Fresh verification after implementation:

```text
python -m compileall src scripts tests
pytest -q tests/test_public_api.py tests/test_ops_scripts.py
```

Result:

```text
26 passed, 1 warning
```

The remaining warning is the existing `speech_recognition` / `aifc` deprecation warning from the document conversion dependency path, not a KMM analysis-layer failure.

Additional server-runtime hardening was added after installed smoke testing:

- `scripts/doc_parse_router.py` now treats missing optional parser commands as a recoverable fallback condition.
- Markdown, text, JSON, CSV, XML, and HTML-like files now have a direct plaintext fallback.
- A regression test covers the missing-command fallback path.

Updated local validation after the router hardening:

```text
pytest -q
python scripts/kmm_e2e_smoke.py
python scripts/sensitive_scan.py
```

Result:

```text
40 passed, 1 warning
kmm_e2e_smoke.py ok: true
scan ok
```

### Why this satisfies the current design goal

Before this change, KMM could collect content and render notes, but the "knowledge" inside those notes existed mostly as human-readable Markdown.

After this change, KMM has a real middle layer:

```text
acquisition -> knowledge analysis object -> note rendering -> retrieval / sync / future sidecar indexing
```

This directly implements the previously documented priority:

- split raw extraction from knowledge modeling
- make note rendering consume a schema
- give sidecar and agents a structured object to identify and call
- preserve readable notes for users

### Remaining work after this implementation

The first version is practical and usable, but deliberately conservative.
The next improvements should be additive behind the same schema:

- optional LLM extractor for higher-quality claims and relation extraction
- optional OCR/ASR block typing for video and image-first sources
- relation extraction for graph edges
- deduplication by knowledge-object fingerprint
- sidecar indexing of `*.knowledge.json`
- retrieval rerank using concepts, claims, and quality score
- evaluation fixtures for Chinese, English, mixed-language, video transcript, and OCR-heavy content

### Next engineering direction

Recommended next task:

1. Teach the memory sidecar to index `*.knowledge.json` beside Markdown notes.
2. Add object-level retrieval in KMM search results.
3. Add optional provider hooks for LLM extraction while keeping deterministic fallback.
4. Add a schema migration policy before `kmm.knowledge_object.v2`.

## 2026-06-30 Next-Phase Full Planning

### Planning authority

This section is a full next-phase plan derived from:

- current repository code state (src/, scripts/, tests/)
- existing continuous development history above
- cross-project integration state with hermes-memory-installer v3.5.1
- GitHub planning documentation (README, collection-pipeline.md)
- server runtime validation results

The plan is organized into three tiers: carry-over (already planned but unfinished), new-priority (P0-P5 phased expansion), and optimization (quality, safety, observability).

---

## Tier A: Carry-Over — Already Planned But Unfinished

These items were documented in earlier sections as  remaining work or next engineering direction and have not yet been completed.

### A1. Server Production Cron Cutover

**Current state**: server KMM installation was validated with KMM_SKIP_CRON=1. Cron entries are still managed outside the repository installer.

**Required actions**:
1. audit current server crontab for KMM-related entries
2. map each entry to repository-managed script or mark as out-of-scope
3. if approved, re-run installer with KMM_SKIP_CRON=0 and explicit KMM_SYNC_REMOTE
4. verify cron entries after cutover
5. record cutover evidence in this document

**Success criteria**:
- crontab -l shows KMM-managed entries (nightly_maintenance, knowledge_discovery, onedrive_bidirectional_sync)
- manual trigger of each cron entry succeeds
- gray validation suite passes with cron enabled

**Risk**: cron misconfiguration could disrupt existing maintenance. Mitigated by gray rollout protocol in docs/GRAY_ROLLOUT.md.

---

### A2. Server Repository Clean-State Sync

**Current state**: server repository working tree is dirty because import-resolution files were copied into place for runtime validation. The latest local fix commit was applied outside the GitHub mainline sync path.

**Required actions**:
1. push remaining local fix commit to GitHub when outbound connectivity is available
2. fast-forward server repository checkout to that GitHub commit
3. verify git status --short returns empty

**Success criteria**:
- server git status is clean
- server git log --oneline -1 matches GitHub HEAD
- server-remote URL is clean public URL (not tokenized)

**Blockers**: outbound GitHub connectivity from server environment.

---

### A3. Formal KMM-Sidecar Knowledge-Object Protocol

**Current state**: KMM produces *.knowledge.json sidecars at schema kmm.knowledge_object.v1. Sidecar knowledge_notes.py indexes rendered Markdown notes but does not consume knowledge JSON objects. Integration is path-and-environment-variable-driven, not contract-driven.

**Required actions**:
1. define versioned shared schema document (proto / JSON Schema / in-repo Markdown)

2. KMM side:
   - stabilize kmm.knowledge_object.v1 as the published contract
   - ensure every generate_note call reliably writes the sidecar JSON
   - add a validation fixture that checks JSON schema compliance

3. Sidecar side:
   - extend knowledge_notes.py to also index *.knowledge.json
   - add knowledge-object-level FTS / metadata columns to knowledge_note_index
   - expose object-level retrieval (facts, concepts, claims, quality score)
   - make knowledge-object index rebuild incremental and signature-gated

4. Shared observability:
   - both projects emit compatible health artifacts referencing the same schema version
   - schema version is recorded in governance_meta

**Success criteria**:
- 	est_kmm_integration.py on sidecar side verifies knowledge JSON indexing
- KMM e2e smoke verifies sidecar JSON output
- retrieval results include source_object_id and schema_version fields when sourced from knowledge JSON

---

### A4. Sidecar Knowledge-Object Indexing

**Current state**: sidecar indexes markdown notes into knowledge_note_index and knowledge_note_index_fts. Knowledge JSON objects are present on disk but not indexed.

**Required actions**:
1. add knowledge_object_index table to governance schema
2. columns: object_id, source_path, schema_version, title, summary, keywords, concepts_json, claims_json, action_items, risks, quality_score, created_at, indexed_at
3. add knowledge_object_index_fts for full-text search over concepts, claims, and summaries
4. extend memory_governance_rebuild.py to rebuild both note index and object index
5. extend 	iered_context_injector.py to fuse object-level results into L3
6. add object provenance to recall output (source_layer, object_id, quality_score)

**Success criteria**:
- governance rebuild indexes both notes and knowledge objects
- tiered recall includes object-level results with schema-aware metadata
- tests verify end-to-end round-trip: KMM generate → sidecar index → sidecar recall

---

### A5. LLM Extractor Hook (Optional, Deterministic Fallback Required)

**Current state**: nalysis.py is purely deterministic and dependency-light. This is correct for the public baseline. An optional LLM extractor was documented as a next improvement.

**Required actions**:
1. add src/knowledge_collector/llm_analyzer.py with provider-agnostic hooks
2. implement LlmKnowledgeAnalyzer that:
   - accepts optional KMM_LLM_PROVIDER env (openai / anthropic / deepseek / etc.)
   - falls back to deterministic KnowledgeAnalyzer when credentials are absent
   - emits the same kmm.knowledge_object.v1 schema
   - adds extractor: llm/openai vs extractor: deterministic provenance
3. add quality.llm_score alongside existing quality.score
4. add test for fallback path when no credentials are configured

**Success criteria**:
- deterministic path unchanged and tested
- LLM path produces richer claims and relations when credentials are provided
- no credential leakage in public repo

---

### A6. Schema Migration Policy

**Current state**: schema version is kmm.knowledge_object.v1. No migration strategy exists for future schema changes.

**Required actions**:
1. document schema migration rules:
   - additive fields are forward-compatible (minor version bump)
   - renamed/removed fields require major version bump
   - schema_version is always written into the JSON payload
2. add migrate_knowledge_object(obj, target_version) function
3. add migration test: 1 → v2 round-trip preserves all data
4. policy: never delete a schema version; add migration path from every version to latest

**Success criteria**:
- schema doc exists in docs/knowledge-object-schema.md
- migration utility is testable
- CI enforces that every KnowledgeObject field has a docstring

---

## Tier B: New Priority — P0 to P5 Phased Expansion

### P0: Production Closure & Multi-Agent Hardening

**Goal**: KMM repository installer becomes the actual source of truth for production KMM runtime. Agent-agnostic assumptions are strengthened.

#### P0.1: Server cutover completion (depends on A1, A2)

- cut over remaining server KMM scripts to repository-installed versions
- document server-side script inventory in docs/SERVER_SCRIPT_MAPPING.md
- record cutover evidence

#### P0.2: Agent-agnostic cleanup

- audit all scripts and docs for Hermes-specific assumptions
- replace HERMES_HOME-only fallbacks with AGENT_HOME as primary contract
- add --agent-home CLI flag to all scripts that currently assume env-var-only
- test with Claude Code, Codex, and Cursor directory layouts

#### P0.3: Fresh-install validation

- add 	ests/test_fresh_install.py:
  - install into empty temp AGENT_HOME
  - verify all managed scripts deployed
  - verify plugin directory structure
  - verify Python imports work from installed location

#### P0.4: Upgrade validation

- add 	ests/test_upgrade.py:
  - install v0.1.0 baseline
  - create test notes
  - upgrade to new version
  - verify existing notes preserved
  - verify new scripts deployed

#### P0.5: Uninstall safety

- add 	ests/test_uninstall.py:
  - verify uninstall removes managed scripts
  - verify uninstall preserves note data
  - verify uninstall preserves user rclone configuration

---

### P1: Document Ingestion Upgrade

**Goal**: move from single-engine MarkItDown to multi-engine scored routing with explicit quality metadata.

**Current state**: doc_parse_router.py supports liteparse → markitdown → pdftotext → plaintext fallback chain.

**Target state**:

`	ext
document → engine selector by file type + size + OCR needs
  → MarkItDown (lightweight, text-first)
  → Docling (layout-aware, tables, complex)
  → MinerU (OCR-heavy, scanned)
  → plaintext fallback
  → quality report per engine attempt
`

#### P1.1: Upgrade doc_parse_router.py

- add engine registry with capability descriptors:
  - supported formats
  - OCR support
  - table preservation
  - layout awareness
  - performance tier
- replace linear chain with scored routing:
  - file extension classification
  - file size tier (small → fast, large → thorough)
  - scanned-content detection heuristic
- persist engine choice and fallback reason

#### P1.2: Integrate Docling

- add docling_project/docling as optional dependency
- add parse_with_docling engine
- emit comparable ContentBlock output to MarkItDown path
- test with table-heavy PDFs and complex DOCX

#### P1.3: Integrate MinerU

- add opendatalab/MinerU as optional dependency
- add parse_with_mineru engine for OCR-heavy PDFs and scanned documents
- add OCR-quality flag in quality report

#### P1.4: Cache reuse by file hash

- compute SHA256 of source file before parsing
- store parse result keyed by (engine, file_hash) in KMM cache directory
- skip re-parse on cache hit
- invalidate when engine version changes

#### P1.5: Batch ingestion CLI

- add python3 -m knowledge_collector.document --batch ./docs/ --recurse --format pdf,docx --output ./out/
- support progress reporting and parallel workers
- support --dry-run to preview routing plan without execution

**Success criteria**:
- doc_parse_router.py routing test covers all engines and fallback paths
- file-hash caching test verifies cache hit avoids re-parse
- batch CLI processes 20+ mixed-format files without error

---

### P2: Retrieval Quality Upgrade

**Goal**: move from basic layer merge to hybrid retrieval with reranking.

**Current state**: 
otes_rag.py and lightweight_recall.py perform parallel layer search with simple score-sorted merge. No query preprocessing, no reranker.

**Target state**:

`	ext
query
  → query rewrite (spelling, expansion, language detection)
  → hybrid search (lexical FTS + vector when available)
  → fusion (RRF or weighted merge)
  → rerank (cross-encoder or API-based)
  → provenance-annotated results
`

#### P2.1: Query preprocessing

- add src/knowledge_collector/query_rewrite.py
- functions:
  - expand_query: add synonyms and related terms
  - detect_language: route to language-appropriate search fields
  - extract_entities: identify named entities for exact-match boost
- deterministic by default; optional LLM-enhanced expansion

#### P2.2: Hybrid retrieval

- integrate qdrant/qdrant-client as optional vector backend
- store note embeddings (from hermes-memory-installer embedding pipeline)
- hybrid search: FTS5 + Qdrant vector → RRF fusion

#### P2.3: Reranker

- add optional Jina AI reranker API integration
- add KMM_RERANKER_API_KEY and KMM_RERANKER_MODEL env
- rerank top-N fused results
- add erank_score alongside etrieval_score in result metadata

#### P2.4: Provenance scoring

- add source_type, source_ref, extraction_quality, ecency to scoring
- add configurable scoring weights via KMM_SEARCH_WEIGHTS env
- add provenance field to every result: {source, layer, retrieval_score, rerank_score, quality_score, timestamp}

#### P2.5: Retrieval evaluation fixtures

- add 	ests/test_retrieval_quality.py
- fixture datasets: English-tech, Chinese-finance, mixed-code, video-transcript
- metrics: recall@5, precision@5, MRR
- baseline regression test: known queries → expected result ordering

**Success criteria**:
- query rewrite improves recall@5 by ≥ 10% on evaluation fixtures
- hybrid search MRR beats single-layer baseline
- reranker preserves or improves top-3 precision
- provenance metadata is parseable and complete

---

### P3: Video Knowledge Pipeline

**Goal**: complete video ingestion from URL to timeline-based mixed-media notes.

**Current state**: collect_video creates basic capture notes. No scene detection, no keyframe OCR, no timeline chunking.

**Target pipeline**:

`	ext
URL → yt-dlp (metadata + subtitle)
  → YouTube Transcript API (if available)
  → Whisper ASR fallback
  → PySceneDetect (scene boundaries)
  → keyframe selection per scene
  → PaddleOCR (frame text extraction)
  → transcript + OCR fusion
  → timeline chunking (30s-120s windows)
  → knowledge analysis per chunk
  → mixed-media note with images + text
`

#### P3.1: Platform adapter framework

- add src/knowledge_collector/video_adapter.py
- VideoAdapter base class:
  - etch_metadata(url) → dict
  - etch_subtitles(url) → list[dict] | None
  - etch_audio(url) → Path
  - platform class attribute
- adapters: YouTubeAdapter, BilibiliAdapter, TikTokAdapter, DouyinAdapter
- fallback: GenericVideoAdapter (yt-dlp only)

#### P3.2: Scene detection and keyframe extraction

- integrate PySceneDetect via subprocess or Python API
- scene_split(video_path) → list[Scene]
- select_keyframes(scenes, max_frames=20) → list[Frame]
- keyframe selection strategy: middle frame of each scene, skip very short scenes

#### P3.3: Frame OCR

- wrap PaddleOCR as optional engine
- ocr_frame(image_path) → str | None
- batch OCR over keyframes with concurrency
- store OCR text per frame with timestamp and confidence

#### P3.4: Timeline chunking

- chunk transcript by sentence boundaries into 30-120 second windows
- attach keyframe and OCR text to each chunk
- generate per-chunk summary

#### P3.5: Mixed-media note generation

- extend generate_note with 	emplate=video:
  - cover section: metadata, executive summary
  - timeline sections: timestamp + summary + keyframe + OCR + claims
  - key takeaways section
  - follow-up links
- embed keyframe images as ![frame](path) in note
- render video-specific knowledge object with timeline blocks

**Success criteria**:
- YouTube video → readable timeline note with screenshots
- Bilibili video → transcript + keyframe note
- short-video (TikTok/Douyin) → OCR-first note
- all paths covered by unit tests and e2e smoke

---

### P4: Defended-Channel Ingestion

**Goal**: add platform-specific adapters for content-heavy channels where direct extraction is fragile.

**Common contract**: every channel adapter emits normalized ContentBlock list — not raw HTML or API response — so downstream processing remains channel-agnostic.

#### P4.1: WeChat Official Account articles

- WechatArticleAdapter in src/knowledge_collector/channels/wechat.py
- extract: title, author, publish date, article body (Markdown), inline images
- normalize to ContentBlock list
- handle request restrictions gracefully (retry, user-agent rotation)

**Reference**: jackwener/wechat-article-to-markdown

#### P4.2: Xiaohongshu image-first pipeline

- XhsAdapter in src/knowledge_collector/channels/xiaohongshu.py
- workflow:
  - user-authorized session capture
  - download post media (images, video covers)
  - OCR each image (PaddleOCR)
  - extract caption/description
  - order images by carousel position
  - generate image-sequence note
- note format: per-image block with image + OCR text + summary

**Reference**: ReaJason/xhs, kohoj/skills (Xiaohongshu → Markdown via OCR)

#### P4.3: Reddit structured thread ingestion

- RedditAdapter in src/knowledge_collector/channels/reddit.py
- prefer structured API paths over HTML scraping
- capture: post title, subreddit, post body, top-N comments, comment hierarchy
- generate discussion-style note:
  - thread summary
  - key viewpoints
  - representative comments with scores
  - related links

**Reference**: socius-org/RedditHarbor, praw-dev/asyncpraw

#### P4.4: Hacker News official API adapter

- HnAdapter in src/knowledge_collector/channels/hackernews.py
- use official HackerNews/API
- capture: story metadata, outbound link, score, comment tree
- generate: story summary, key discussion themes, notable technical takeaways

#### P4.5: CSDN article adapter

- CsdnAdapter in src/knowledge_collector/channels/csdn.py
- normalize article body to Markdown
- preserve code blocks, headings, images, references
- auto-classify article topic into KMM note taxonomy

#### P4.6: Channel adapter registry

- add src/knowledge_collector/channels/__init__.py with CHANNEL_REGISTRY
- collect_article auto-routes to channel adapter when source matches a registered platform
- channel adapters are importable but execution is guarded by availability of platform-specific dependencies

---

### P5: Scheduling, Observability & MCP Exposure

#### P5.1: Managed workflow engine

- integrate lightweight workflow orchestrator (recommend dagu-org/dagu)
- wrap KMM critical tasks as DAG nodes:
  - knowledge_discovery.py
  - 
ightly_maintenance.py
  - ook_cache_manager.py
  - onedrive_bidirectional_sync.sh
- add per-task: retries, timeout, last-success marker, dead-letter handling
- cron is the fallback when orchestrator is unavailable

#### P5.2: KMM health artifacts

- add scripts/kmm_health_check.py:
  - last knowledge discovery timestamp
  - last sync timestamp and status
  - note count by domain
  - book cache index freshness
  - ingestion success/failure rate (last 24h)
  - retrieval hit distribution (by layer)
- output: $AGENT_HOME/knowledge/kmm-health.json
- sidecar lert_queue.py can consume this health artifact

#### P5.3: Observability cross-integration

- KMM emits kmm-health.json into shared agent health directory
- sidecar lert_queue.py picks up KMM health artifacts
- sidecar metrics_dashboard.py adds KMM panel
- sidecar slo_rollup.py includes KMM metrics

#### P5.4: MCP server for KMM

- add src/mcp_server.py with MCP tools:
  - kmm_collect_web(url) → note_id, knowledge_object
  - kmm_search(query, layers) → fused results with provenance
  - kmm_discover(days) → new note list
  - kmm_sync_status() → cloud sync freshness
  - kmm_analyze(text, source_type) → knowledge object
- KMM_MCP_ENABLED=1 activates MCP mode
- MCP server binds to configurable port, 127.0.0.1 by default
- supports stdio transport for direct agent integration

#### P5.5: Agent capability discovery

- add capability.yaml at KMM root:
  `yaml
  kmm:
    version: 0.1.0
    capabilities:
      - id: kmm.collect.web
        description: Collect web page content into structured notes
        input: {url: string}
        output: {note_id: string, knowledge_path: string}
      - id: kmm.search
        description: Multi-layer fused knowledge search
        input: {query: string, layers: [string]}
        output: {results: [{source, title, score, provenance}]}
  `
- sidecar reads capability.yaml for automatic tool registration
- agents can discover KMM capabilities without prior knowledge of script paths

---

## Tier C: Optimization Targets

### C1. Performance

| Item | Current | Target | Approach |
|------|---------|--------|----------|
| Recall latency (cold) | ~15s (Hindsight timeout) | <5s | parallel + timeout + cache |
| Recall latency (warm) | ~2s | <500ms | query cache by governance signature |
| Ingestion throughput | single-threaded | N workers | ThreadPoolExecutor for batch collect |
| Knowledge-object dedup | none | content-hash fingerprint | SHA256(title+source_ref+content) |
| Book cache rebuild | full rescan | incremental | signature-gated as in knowledge_notes.py |

### C2. Test Coverage

| Item | Current | Target |
|------|---------|--------|
| Total tests | 40 | 60+ |
| Fresh install test | none | test_fresh_install.py |
| Upgrade test | none | test_upgrade.py |
| Uninstall safety test | assertion-only | test_uninstall.py |
| Sync behavior test | e2e smoke only | test_sync_behavior.py (dry-run, conflict, retry) |
| Recall quality regression | none | test_retrieval_quality.py with fixtures |
| Knowledge JSON validation | implicit | pytest schema compliance check |
| Chinese-language fixtures | none | zh + en + mixed test fixtures for analysis and retrieval |

### C3. Security & Privacy

| Item | Current | Target |
|------|---------|--------|
| Sensitive scan in CI | yes (ci.yml runs sensitive_scan.py) | keep |
| Knowledge JSON path leak scan | none | add path-pattern check to sensitive_scan.py |
| Installer does not write server paths | verified | add regression test |
| Recall output sanitization | basic ([:400] truncation) | strip paths matching AGENT_HOME from recall output |
| Credential injection | env-only | verify no hardcoded creds in CI check |

### C4. Documentation

| Item | Current | Target |
|------|---------|--------|
| README vs code match | partial (claims broader than repo-backed) | README describes only repository-backed features |
| API reference | README tables only | add docs/api-reference.md with per-function doc |
| Schema doc | inline in analysis.py | add docs/knowledge-object-schema.md |
| Channel adapter guide | none | add docs/channel-adapters.md |
| Video pipeline guide | collection-pipeline.md only | add docs/video-pipeline.md |

### C5. Release Engineering

| Item | Current | Target |
|------|---------|--------|
| CI workflow | basic test + scan | add fresh-install, upgrade, schema-validation jobs |
| Release version | 0.1.0 (src/__init__.py) mismatched with 0.0.2 (GitHub release) | unify to single version source |
| Changelog | GitHub release notes only | add CHANGELOG.md following Keep a Changelog |
| Release checklist | present (docs/RELEASE_CHECKLIST.md) | keep updated per release |
| Gray rollout | documented | automate gray-validation suite run |

---

## Implementation Sequence

The recommended build order respects dependencies between tiers:

`
Phase 1 (Week 1-2): Carry-Over + P0
  A1 → A2 → A3 → P0.2 → P0.1 → P0.3 → P0.4 → P0.5

Phase 2 (Week 3-4): P1 Document Ingestion
  P1.1 → P1.2 → P1.3 → P1.4 → P1.5

Phase 3 (Week 5-6): A4 + A5 + A6 (Sidecar Integration)
  A4 → A5 → A6

Phase 4 (Week 7-8): P2 Retrieval
  P2.1 → P2.2 → P2.3 → P2.4 → P2.5

Phase 5 (Week 9-10): P3 Video
  P3.1 → P3.2 → P3.3 → P3.4 → P3.5

Phase 6 (Week 11-12): P4 Defended Channels
  P4.1 → P4.4 → P4.2 → P4.3 → P4.5 → P4.6

Phase 7 (Week 13-14): P5 Observability + MCP
  P5.1 → P5.2 → P5.3 → P5.4 → P5.5

Phase 8 (Ongoing): Optimization
  C1 → C2 → C3 → C4 → C5 (parallel, continuous)
`

## Immediate Next Actions (Today/Tomorrow)

1. **[ ]** Push remaining local fix commit to GitHub
2. **[ ]** Fast-forward server repo to clean state
3. **[ ]** Add .benchmarks/ to .gitignore (done 2026-06-30)
4. **[ ]** Run full validation: pytest -q, python scripts/kmm_e2e_smoke.py, python scripts/sensitive_scan.py
5. **[ ]** Begin Phase 1: audit server cron entries (A1)

## Phase Gate Criteria

Each phase is gated by the following before proceeding to the next:

- All tests pass (pytest -q, kmm_e2e_smoke.py)
- Sensitive scan passes (sensitive_scan.py)
- Compile check passes (python -m compileall src scripts tests)
- This document updated with implementation notes
- GitHub and server in sync

