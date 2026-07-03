# Roadmap

This project starts as a reliable URL-to-Markdown extractor and can grow into a small research stack.

## Phase 1: Stable Extraction

- Public status URL support.
- X Article block parsing.
- Batch mode.
- Metadata JSON.
- Raw JSON preservation.
- Codex skill packaging.

## Phase 2: Discovery

- Named X source lists with tags and notes.
- Search-engine based discovery of candidate X status links.
- Domain/topic watchlists.
- Deduplication by tweet id and article id.
- Per-source metadata normalization.

## Phase 3: Local Research Corpus

- Store Markdown artifacts in a predictable folder layout.
- Add lightweight JSONL index.
- Add summary, tags, and topic fields.
- Export JSON Feed and RSS for downstream readers.
- Provide a Chinese local web app for creating projects, capturing X URLs, and maintaining a `meta.md` article per project.
- Support recurring research workflows for business and AI monitoring.

## Phase 4: Official X MCP Bridge

- Optional adapter for a locally configured official X MCP server.
- Authenticated search and account-specific retrieval with user credentials.
- Same output shape: Markdown + metadata + raw source.

## Phase 5: Agent Workflows

- Codex skill commands for:
  - fetch this link,
  - summarize this author,
  - build a weekly trend digest,
  - compare posts across a topic,
  - export research notes.
