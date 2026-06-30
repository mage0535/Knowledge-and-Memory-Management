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
