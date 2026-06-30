# KMM Knowledge Object Schema

**Version**: `kmm.knowledge_object.v1`
**Status**: stable
**File extension**: `.knowledge.json`

This schema defines the machine-readable knowledge object produced by `analyze_material()` and stored alongside Markdown notes by `generate_note()`.

## Schema

```json
{
  "schema_version": "kmm.knowledge_object.v1",
  "object_id": "ko-{slug}-{sha256[:16]}",
  "title": "string",
  "source_type": "web | video | article | document | book | note",
  "source_ref": "URL or file path",
  "language": "zh | en | unknown",
  "summary": "1-3 sentence extractive summary",
  "keywords": ["string"],
  "concepts": [
    {
      "name": "concept name",
      "evidence": "sentence containing concept",
      "weight": 1.0
    }
  ],
  "claims": [
    {
      "text": "claim sentence",
      "evidence": "supporting sentence",
      "confidence": 0.62
    }
  ],
  "action_items": ["action sentence"],
  "open_questions": ["question sentence"],
  "risks": ["risk sentence"],
  "timeline": [
    {
      "date": "YYYY-MM-DD or partial",
      "text": "timeline sentence"
    }
  ],
  "content_blocks": [
    {
      "type": "text | transcript | ocr | image",
      "text": "block text content",
      "order": 0,
      "source_ref": "string",
      "metadata": {}
    }
  ],
  "quality": {
    "score": 0.0-1.0,
    "confidence": "high | medium | low",
    "char_count": 0,
    "block_count": 0,
    "claim_count": 0,
    "keyword_count": 0
  },
  "created_at": "ISO 8601 UTC",
  "metadata": {
    "tags": ["string"],
    "domain": "personal | shared | archive",
    "extractor": "deterministic | llm/{provider}",
    "llm_score": 0.0-1.0
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | yes | Version identifier for migration compatibility |
| `object_id` | string | yes | Unique ID: `ko-{slugified title}-{sha256 trunc 16}` |
| `title` | string | yes | Note title |
| `source_type` | string | yes | Origin type: web, video, article, document, book, note |
| `source_ref` | string | no | Source URL or file path |
| `language` | string | yes | Detected language: zh, en, unknown |
| `summary` | string | yes | Extractive 1-3 sentence summary |
| `keywords` | list[string] | yes | Top N keywords by frequency |
| `concepts` | list[object] | yes | Named concepts with evidence |
| `claims` | list[object] | yes | Factual claims with confidence |
| `action_items` | list[string] | yes | Marked action sentences (may be empty) |
| `open_questions` | list[string] | yes | Sentences ending with ? or ？(may be empty) |
| `risks` | list[string] | yes | Risk-marked sentences (may be empty) |
| `timeline` | list[object] | yes | Date-pattern sentences (may be empty) |
| `content_blocks` | list[object] | yes | Normalized content blocks from source adapter |
| `quality.score` | float | yes | Composite quality score 0.0-1.0 |
| `quality.confidence` | string | yes | Threshold: high (>=0.75), medium (>=0.45), low |
| `metadata.extractor` | string | no | "deterministic" or "llm/{provider}" |

## Quality Scoring

| Factor | Score contribution |
|--------|------------------|
| char_count >= 120 | +0.30 |
| block_count >= 1 | +0.20 |
| claims present | +0.25 |
| keywords >= 3 | +0.15 |
| char_count >= 1000 | +0.10 |

Max score: 1.0

## Deterministic Extractor

The default analyzer (`KnowledgeAnalyzer`) uses no external LLM:

- **Keyword extraction**: regex tokenization + frequency ranking with stopword filter
- **Concept detection**: keyword-to-sentence evidence mapping
- **Claim detection**: marker-word pattern matching (bilingual: en + zh)
- **Action detection**: action-marker sentence filtering
- **Risk detection**: risk-marker sentence filtering
- **Timeline**: regex date pattern matching
- **Summary**: keyword-weighted sentence selection
- **Language detection**: CJK character ratio heuristic

## Migration Policy

- Fields added: minor version bump, forward-compatible
- Fields renamed/removed: major version bump, `migrate_knowledge_object()` required
- `schema_version` always written into payload
- No schema version ever deleted; migration path from every version to latest

## Sidecar Integration

KMM writes `*.knowledge.json` alongside `*.md` notes. The memory sidecar indexes:

- `object_id` for dedup
- `schema_version` for compatibility
- `title`, `summary`, `keywords` for search
- `concepts`, `claims`, `action_items`, `risks` for structured retrieval
- `quality.score` for ranking
- `created_at` for recency

Sidecar retrieves knowledge objects alongside Markdown notes, exposing `source_layer: "knowledge"` and `source_object_id` in fused recall results.
