# KMM API Reference

Version 0.1.0

## knowledge_collector

### `collect_web(url, strategy="auto") -> CollectionResult`

Collect web page content and generate a structured note.

```python
from knowledge_collector import collect_web
result = collect_web("https://example.com/article")
print(result.note_path)  # path to generated note
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | str | required | Target URL |
| `strategy` | str | `"auto"` | auto / simple_page / dynamic_page / anti_bot_page |

Returns `CollectionResult(source_type, title, content_preview, url, note_path, gbrain_slug, extractor, metadata)`.

---

### `collect_video(url) -> CollectionResult`

Create a structured capture note from a video URL.

```python
from knowledge_collector import collect_video
result = collect_video("https://www.youtube.com/watch?v=xxx")
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | str | required | Video URL (YouTube, Bilibili, etc.) |

Returns `CollectionResult` with `metadata.video_id` and `subtitles` fields.

---

### `collect_article(source, keyword) -> CollectionResult`

Collect article content by source platform and keyword or URL.

```python
from knowledge_collector import collect_article
result = collect_article("wechat", "weekly digest")
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | str | required | Source platform (wechat, web, etc.) |
| `keyword` | str | required | Search keyword or URL |

---

### `collect_document(path) -> CollectionResult`

Collect document content (PDF, DOCX, MD, etc.) via MarkItDown conversion.

```python
from knowledge_collector import collect_document
result = collect_document("./report.pdf")
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | str | required | Local file path |

---

### `collect_book(path) -> dict`

Trigger book-to-skill refinement pipeline.

```python
from knowledge_collector import collect_book
result = collect_book("./machine-learning.pdf")
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | str | required | PDF or EPUB file path |

---

### `generate_note(material, template="article", note_title=None) -> dict`

Generate a Markdown note and knowledge JSON sidecar.

```python
from knowledge_collector import generate_note
note = generate_note(
    {"title": "My Note", "content": "KMM extracts claims and concepts."},
    template="note",
)
print(note["note_path"])      # path to .md
print(note["knowledge_path"]) # path to .knowledge.json
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `material` | dict\|str | required | `{title, content, domain, tags}` or raw string |
| `template` | str | `"article"` | article / note / video / web |
| `note_title` | str\|None | None | Override title |

Returns `{note_id, note_path, knowledge_path, domain, title, analysis, dedup}`.  
`dedup: True` when note already existed with same content hash and was returned instead of duplicated.

---

### `analyze_material(material, source_type="article") -> dict`

Analyze source material and return a knowledge object.

```python
from knowledge_collector import analyze_material
knowledge = analyze_material(
    {"title": "Layered Recall", "content": "Layered recall is a memory architecture."},
    source_type="note",
)
print(knowledge["object_id"])      # ko-layered-recall-{sha256[:16]}
print(knowledge["keywords"])       # ["layered", "recall", "memory"]
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `material` | dict\|str\|None | required | Source material |
| `source_type` | str | `"article"` | Type hint for analysis |

Returns `kmm.knowledge_object.v1` dict.

---

### `migrate_knowledge_object(obj, target_version) -> dict`

Migrate a knowledge object between schema versions.

```python
from knowledge_collector.analysis import migrate_knowledge_object
obj = migrate_knowledge_object(old_obj, "kmm.knowledge_object.v2")
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `obj` | dict | required | Source knowledge object |
| `target_version` | str | required | Target schema version string |

Raises `ValueError` if no migration path exists.

---

### `render_knowledge_note(knowledge, include_source=True) -> str`

Render a knowledge object as readable Markdown.

```python
from knowledge_collector import render_knowledge_note
md = render_knowledge_note(knowledge, include_source=True)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `knowledge` | dict | required | Knowledge object dict |
| `include_source` | bool | True | Include source content at end |

---

## notes_rag

### `create_note(title, content, domain="personal", tags=None) -> dict`

Create a note and returns its location info plus analysis.

```python
from notes_rag import create_note
note = create_note("Agent Memory", "Layered memory design", domain="shared")
```

### `search_notes(query, domains=None) -> list[dict]`

Multi-layer fused search across local notes, state FTS5, Hindsight, gbrain.

```python
from notes_rag import search_notes
results = search_notes("agent memory architecture", domains=["shared"])
for r in results:
    print(r["source"], r["title"], r["score"])
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | str | required | Search query |
| `domains` | list[str]\|None | all | personal, shared, archive |

Returns list of `{title, content, score, url, source}`.

### `sync_notes_to_cloud(remote=None) -> dict`

Sync local notes to configured cloud remote.

```python
from notes_rag import sync_notes_to_cloud
result = sync_notes_to_cloud()  # uses KMM_SYNC_REMOTE env
```

---

## cloud_sync

### `list_cloud_drives() -> list[str]`

List configured rclone remotes.

```python
from cloud_sync import list_cloud_drives
drives = list_cloud_drives()
```

### `sync_to_cloud(local, remote) -> subprocess.CompletedProcess`

Copy local directory to cloud. `remote` format: `"remote:path"`.

### `sync_from_cloud(remote, local) -> subprocess.CompletedProcess`

Copy from cloud to local directory.

### `bidirectional_sync(remote, local=None, resync=False) -> subprocess.CompletedProcess`

Bisync between local and cloud. First run requires `resync=True`.

```python
from cloud_sync import bidirectional_sync
bidirectional_sync("onedrive:notebooks/notes", local="/data/notes", resync=True)
```

---

## knowledge_augmentation

### `AugmentedSearch.search(query, domain="", local_only=False, web_only=False) -> dict`

Local-first search with AnySearch web fallback.

```python
from knowledge_augmentation import AugmentedSearch
searcher = AugmentedSearch()
result = searcher.search("China GDP 2026", domain="finance")
print(result["source"])  # "local", "web", or "hybrid"
```

Returns `{query, source, local_weight, results, augmented}`.

### `AugmentedSearch.list_domains() -> list[dict]`

List available AnySearch vertical domains.

---

## Compiled Checksums

```bash
python -m compileall src scripts tests
pytest -q                        # 40 passed
python scripts/kmm_e2e_smoke.py  # end-to-end validation
python scripts/sensitive_scan.py # privacy scan
```
