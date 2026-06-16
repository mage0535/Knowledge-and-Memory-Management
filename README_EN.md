<div align="center">

# Knowledge and Memory Management

**Go beyond "remembering" — a full-chain plugin for knowledge collection → note generation → semantic search → cloud sync.**

> 📦 **Positioning**: Capability extension layer for [hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer).
> The base handles "remembering". KMM handles "where knowledge comes from and how to use it".

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![yt-dlp 2026.3](https://img.shields.io/badge/yt--dlp-2026.3-green)](https://github.com/yt-dlp/yt-dlp)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/mage0535/Knowledge-and-Memory-Management/pulls)

[**中文文档**](README.md) | [**Collection Pipeline**](docs/collection-pipeline.md)

</div>

---

## Architecture Overview

```
Collection Layer (40+ tools)  →  Analysis Layer (AI)  →  Storage Layer (3-tier memory)
   │                              │                       │
   ├─ Web engines (9)             ├─ Auto note generation  ├─ Hot (Memory tool)
   ├─ Video engines (12)          ├─ Knowledge graph       ├─ Warm (Hindsight, 10K nodes)
   ├─ Articles/Content (10)       ├─ NLI fact checking     └─ Cold (gbrain, 11K pages)
   ├─ Documents/OCR (9)           ├─ Knowledge discovery
   ├─ Knowledge analysis (7)      └─ Book auto-refinement
   └─ Knowledge management (4)
                                             ┌─ OneDrive / Google Drive
                                             ├─ Alibaba Cloud Drive / Baidu Netdisk
              Cloud Sync (rclone, 12+ drivers)──┼─ Dropbox / Mega / pCloud
                                             ├─ WebDAV / S3 / Tianyi Cloud
                                             └─ More (all rclone-supported drivers)
```

---

## Modules

| Module | Directory | Description |
|--------|-----------|-------------|
| **Knowledge Collector** | `src/knowledge_collector/` | 9 sub-modules covering web/video/articles/documents/analysis/note generation/refinement/knowledge management |
| **Notes RAG** | `src/notes_rag/` | Semantic search, vector retrieval, 3-tier context recall |
| **Cloud Sync** | `src/cloud_sync/` | rclone unified driver, 12+ cloud storage bidirectional sync |
| **SenseNova Engine** | `src/sensenova/` | PDF/PPT/Word intelligent document analysis |
| **Knowledge Augmentation** | `src/knowledge_augmentation/` | Local-first + AnySearch web fallback |
| **Pipeline Docs** | `docs/collection-pipeline.md` | **40+ tools** with detailed descriptions and pipeline diagrams |
| **Tool Versions** | `docs/tool-versions.md` | Verified toolchain version table |
| **Quick Start** | `docs/quick-start.md` | Installation and first collection |

---

## 40+ Collection & Analysis Tools

### 🌐 Web Collection (9 engines)

| Tool | Type | Rating | Use Case |
|------|------|--------|----------|
| **Scrapling** | MCP | ⭐⭐⭐⭐⭐ | Anti-detection scraping, Cloudflare bypass, stealthy/dynamic/http modes |
| **Chrome DevTools** | MCP | ⭐⭐⭐⭐⭐ | Full browser automation, JS execution, network analysis |
| **GStack Browser** | Built-in | ⭐⭐⭐⭐⭐ | Hermes native browser + visual analysis |
| **knowledge_fetch_router** | Script | ⭐⭐⭐⭐ | Smart routing (trafilatura→readability→Crawl4AI) |
| **knowledge_site_crawler** | Script | ⭐⭐⭐⭐ | Crawlee same-domain batch crawler |
| **obscura_fetch_bridge** | Bridge | ⭐⭐⭐ | Dynamic page Markdown extraction |
| **opensquilla_bridge** | Bridge | ⭐⭐⭐ | Lightweight sidecar collection |
| **web_extract** | Built-in | ⭐⭐ | Pure HTTP content extraction |
| **ripgrep_kb_scan** | Script | ⭐⭐ | Knowledge base dedup pre-screening |

### 🎬 Video Collection (12 tools)

| Tool | Type | Rating | Use Case |
|------|------|--------|----------|
| **douyin_video_intake** | Script | ⭐⭐⭐⭐⭐ | Douyin metadata + subtitles + ASR |
| **douyin_batch_transcriber** | Script | ⭐⭐⭐⭐⭐ | Douyin batch multi-video concurrent transcription |
| **social_video_intake** | Script | ⭐⭐⭐⭐⭐ | Universal social video unified entry |
| **universal-video-analyzer** | Skill | ⭐⭐⭐⭐⭐ | Multi-language OCR/face/quality/BGM/emotion |
| **media_transcriber_wrapper** | Script | ⭐⭐⭐⭐ | Universal media transcription wrapper |
| **yt-dlp** | CLI | ⭐⭐⭐⭐ | 1000+ sites video download |
| **Whisper ASR** | Engine | ⭐⭐⭐⭐ | 99+ language speech-to-text |
| **EasyOCR** | Engine | ⭐⭐⭐ | Video keyframe text extraction |
| **PaddleOCR** | Engine | ⭐⭐⭐⭐ | 70k⭐ high-accuracy OCR |
| **FFmpeg** | CLI | ⭐⭐⭐ | Video split/convert/audio extraction |
| **Tesseract OCR** | CLI | ⭐⭐⭐ | Open-source OCR (Chinese support) |
| **YouTube Analytics** | Skill | ⭐⭐⭐⭐ | Channel/video data analysis |

### 📄 Documents/OCR (9 tools) — with SenseNova

| Tool | Rating | Description |
|------|--------|-------------|
| **SenseNova PDF Analysis** | ⭐⭐⭐⭐⭐ | Text+scan PDFs, tables/charts/multi-page extraction |
| **SenseNova PPT Analysis** | ⭐⭐⭐⭐⭐ | Full slide text/tables/charts/embedded images |
| **SenseNova Word Analysis** | ⭐⭐⭐⭐⭐ | Body/tables/highlights/formatting/multi-document comparison |
| **umi_ocr_bridge** | ⭐⭐⭐⭐ | Chinese OCR enhancement bridge |
| **doc_parse_router** | ⭐⭐⭐⭐ | Multi-format routing (PDF/HTML/MD/Office) |
| **Magic-PDF** | ⭐⭐⭐⭐ | PDF → Markdown conversion |
| **MinerU** | ⭐⭐⭐⭐ | Document content intelligent extraction |
| **PaddleOCR** | ⭐⭐⭐⭐ | Baidu open-source high-accuracy OCR (70k⭐) |
| **book_cache_manager** | ⭐⭐⭐⭐ | 710+ book index + on-demand cache + auto-refinement |

### 🔬 Knowledge Analysis (7 tools)

web_search / web_extract / NLI fact checking / comment summarization / news enrichment / keyword extraction / cross-validation

### 🧠 Knowledge Management (4 tools) — NEW

| Tool | Rating | Description |
|------|--------|-------------|
| **knowledge_discovery** | ⭐⭐⭐⭐⭐ | Weekly auto-scan OneDrive→local→gbrain ingestion |
| **lightweight_recall** | ⭐⭐⭐⭐⭐ | 3-tier cross-layer recall (FTS5 + Hindsight + gbrain) |
| **onedrive_bidirectional_sync** | ⭐⭐⭐⭐⭐ | OneDrive bidirectional incremental sync (every 4h) |
| **nightly_maintenance** | ⭐⭐⭐⭐⭐ | Night maintenance orchestrator (discovery + orphan links + compact) |

---

## Quick Install

```bash
# Prerequisite: hermes-memory-installer (gbrain + Hindsight) already installed
source ~/.hermes/hermes-agent/.venv/bin/activate

# Clone the repo
git clone https://github.com/mage0535/Knowledge-and-Memory-Management.git
cd Knowledge-and-Memory-Management

# Run installer
bash install.sh
```

The installer automatically:
1. Detects Hermes environment (venv, gbrain port 8787, Hindsight port 8890)
2. Installs/upgrades Python dependencies (yt-dlp, scrapling, paddleocr, etc.)
3. Detects system tools (ffmpeg, tesseract, rclone)
4. Configures cloud drive bidirectional sync rules
5. Registers scheduled knowledge collection cron jobs
6. Configures knowledge discovery auto pipeline

---

## Usage

### Document Analysis

```bash
# SenseNova PDF — supports text & scanned PDFs
python3 sensenova_dispatcher.py pdf report.pdf

# SenseNova PPT — full slide extraction
python3 sensenova_dispatcher.py ppt presentation.pptx

# SenseNova Word — body + tables + formatting
python3 sensenova_dispatcher.py word document.docx
```

### Book Auto-Refinement

```bash
# Full pipeline (recommended)
python3 book_to_skill.py all book.pdf --name machine-learning

# Auto-triggered via cache manager
python3 book_cache_manager.py cache book.pdf
# → automatically triggers refinement pipeline
```

### Knowledge Retrieval

```bash
# 3-tier recall (FTS5 + Hindsight + gbrain)
python3 lightweight_recall.py --query "Agent memory system design" --limit 10

# gbrain semantic search
gbrain search "knowledge graph" --limit 5
```

### Knowledge Discovery (automated)

Runs automatically every Sunday. Manual trigger:

```bash
python3 knowledge_discovery.py
```

---

## Cloud Sync

Supports 12+ cloud storage drivers via rclone:

| Cloud | Auth | Sync Mode |
|-------|------|-----------|
| OneDrive | OAuth | Bidirectional incremental (every 4h) |
| Google Drive | OAuth | One-way + on-demand |
| Alibaba Cloud Drive | Token | One-way backup |
| Baidu Netdisk | OAuth | One-way backup |
| Dropbox / Mega / pCloud / Tianyi Cloud / 123 Cloud / S3 / WebDAV | Per rclone standard | Configurable |

---

## Knowledge Augmentation

**When local notes aren't enough, auto-fallback to AnySearch vertical search.**

```
User search → search_notes("BYD 2026Q1 earnings")
    │
    ├─ Local hit (score ≥ 0.6) → return note results
    │
    └─ Local insufficient (score < 0.6) → AnySearch vertical search
         ├─ domain=finance (financial data)
         ├─ domain=academic (papers)
         └─ Results auto-tagged source: web, importable to notes
```

---

## API Reference

### knowledge_collector

| Function | Description |
|----------|-------------|
| `collect_web(url)` | Collect web content → knowledge base |
| `collect_video(url)` | Collect video content (OCR+ASR) |
| `collect_article(source, keyword)` | Collect article content |
| `generate_note(material, template)` | Generate structured note |

### notes_rag

| Function | Description |
|----------|-------------|
| `create_note(title, content, domain)` | Create note |
| `search_notes(query, domains)` | Cross-domain search (3-tier recall) |
| `sync_notes_to_cloud()` | Sync notes to cloud |

### cloud_sync

| Function | Description |
|----------|-------------|
| `list_cloud_drives()` | List configured cloud drives |
| `sync_to_cloud(local, remote)` | Local → cloud |
| `sync_from_cloud(remote, local)` | Cloud → local |

---

## Changelog

### v0.0.2 (2026-06-16)

- **Collection pipeline v2.0**: Tools expanded from 30+ to **40+**
- **SenseNova document engine**: PDF/PPT/Word intelligent analysis
- **Knowledge management module**: Auto-discovery + 3-tier recall + bidirectional cloud sync
- **Video collection expanded**: douyin_batch_transcriber + media_transcriber_wrapper
- **10 cron compact system**: 34→10, night maintenance orchestrates all maintenance
- **Knowledge refinement auto-trigger**: `book_cache_manager` download auto-triggers refinement

### v0.0.1 (2026-06-04)

- Initial release: knowledge collection, notes RAG, cloud sync full chain
- 30+ collection & analysis tools panorama
- rclone 12+ cloud drive unified interface

---

## License

MIT License © 2026

---

## Related Projects

- **[hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer)** — Memory base layer. gbrain + Hindsight + 3-tier recall. Agent-agnostic memory sidecar that handles the "remembering" part. KMM extends it.
- [hermes-agent](https://github.com/nousresearch/hermes-agent) — Hermes Agent framework
- [gbrain](https://github.com/nousresearch/gbrain) — Knowledge graph engine
- [book-to-skill](https://github.com/virgiliojr94/book-to-skill) — Knowledge structuring concept (inspiration)
