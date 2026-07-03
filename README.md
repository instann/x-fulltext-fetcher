<p align="center">
  <img src="assets/hero-banner.png" alt="X Fulltext Fetcher banner" width="100%">
</p>

<p align="center">
  <strong>English</strong> / <a href="./README.zh-CN.md">简体中文</a>
</p>

# X Fulltext Fetcher

> A local-first X/Twitter article project library for capturing public X links into Markdown, project collections, and living meta articles.

X Fulltext Fetcher helps you collect public posts and X Articles for business, AI, market, and creator-research workflows. Start the local app, create a project, paste a public X status URL, and the article is fetched into that project as Markdown. Each project keeps a `meta.md` article that accumulates the project library for later summarization.

It does **not** bypass authentication, paywalls, private accounts, platform access controls, or copyright rules.

## Why This Exists

X contains many useful long-form posts and Articles, but public pages often require login or render content through client-side data. For legitimate research, personal archiving, and AI-assisted note-taking, this project provides a reproducible workflow:

- Fetch a public X status URL.
- Detect whether it contains an X Article.
- Convert available text blocks into Markdown.
- Preserve metadata and raw JSON when needed.
- Create local research projects.
- Paste one public X status URL and save it into the selected project.
- Maintain a project-level `meta.md` article for later synthesis.
- Build a local digest, JSONL index, JSON Feed, and RSS feed when needed.
- Use the bundled Codex skill for repeatable agent workflows.

## Features

- **URL to Markdown**: Convert public `/status/<id>` links into readable Markdown.
- **X Article support**: Parse `tweet.article.content.blocks` when available.
- **Batch mode**: Process a list of links into a local corpus folder.
- **Metadata output**: Save title, source URL, tweet id, article id, block count, cover image, and API URL.
- **Local project app**: Run a Chinese web UI for project creation, URL capture, article display, and meta-article preview.
- **Source lists**: Maintain named X research collections in `examples/sources.json`.
- **Digest and feed output**: Generate Markdown digests, JSONL indexes, JSON Feed, and RSS.
- **Static dashboard**: Browse and mark research items in `web/index.html`.
- **Raw source preservation**: Optionally store raw JSON for later auditing.
- **Codex skill included**: Installable skill for future agent-driven research workflows.
- **Extensible architecture**: Add adapters for search, official X MCP, indexing, or monitoring.

## Quick Start

Clone the repository and start the local app:

```powershell
git clone https://github.com/instann/x-fulltext-fetcher.git
cd x-fulltext-fetcher
python scripts/run_app.py
```

Open:

```text
http://127.0.0.1:8767/
```

In the app:

1. Create a project.
2. Paste a public X status URL.
3. Click `抓取并收录`.
4. Review the article list and the project `meta.md` preview.

Fetch one public X status URL from the CLI:

```powershell
python scripts/fetch_x_fulltext.py "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md --metadata
```

Batch mode:

```powershell
python scripts/fetch_x_fulltext.py --batch examples/links.txt --out-dir outputs/corpus --metadata-out outputs/corpus/metadata.json --raw-json-dir outputs/raw
```

Research feed mode:

```powershell
python scripts/fetch_x_fulltext.py --sources examples/sources.json --out-dir outputs/research --digest-out outputs/research/digest.md --index-out outputs/research/index.jsonl --feed-json web/feed.json --feed-rss outputs/research/feed.xml
```

Install as a local Python package:

```powershell
python -m pip install -e .
x-fulltext-fetch "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md
x-fulltext-app
```

## Example Output

```markdown
# Super useful Article title

> Article preview...

Source: https://x.com/user/status/123
Article ID: 456

## Section
- Bullet
- Bullet
```

## Repository Layout

```text
x-fulltext-fetcher/
|-- assets/                       # README visuals
|-- docs/
|   |-- LEGAL.md                  # compliance and acceptable use
|   |-- METHODS.md                # endpoint notes and fallback strategy
|   `-- ROADMAP.md                # planned MCP-like extensions
|-- examples/
|   |-- links.txt                 # batch input example
|   `-- sources.json              # named X research sources
|-- scripts/
|   |-- fetch_x_fulltext.py       # standalone CLI script
|   `-- run_app.py                # local web app launcher
|-- skills/
|   `-- x-fulltext-fetcher/       # Codex skill package
|-- src/
|   `-- x_fulltext_fetcher/       # Python package entrypoint
|-- web/                          # Chinese local project app frontend
`-- tests/
```

## Codex Skill

The bundled skill lives in:

```text
skills/x-fulltext-fetcher
```

To install it for Codex, copy that folder into your Codex skills directory:

```powershell
Copy-Item -Recurse -Force .\skills\x-fulltext-fetcher "$env:USERPROFILE\.codex\skills\x-fulltext-fetcher"
```

Then ask Codex:

```text
Use $x-fulltext-fetcher to fetch and summarize this X Article link: ...
```

## How It Works

The current primary adapter uses:

```text
https://api.fxtwitter.com/{screen_name}/status/{status_id}
```

Observed useful fields:

- `tweet.raw_text.text`
- `tweet.article.title`
- `tweet.article.preview_text`
- `tweet.article.content.blocks`
- `tweet.article.content.entityMap`
- `tweet.article.cover_media.media_info.original_img_url`

See [docs/METHODS.md](docs/METHODS.md) for alternatives and limitations.

## Update Plan

This project starts as a reliable URL-to-Markdown extractor and will grow toward a small research stack.

### Phase 1: Stable Extraction

- Public status URL support.
- X Article block parsing.
- Batch mode.
- Metadata JSON.
- Raw JSON preservation.
- Codex skill packaging.

### Phase 2: Discovery

- Named X source lists and topic tags.
- Search-engine based discovery of candidate X status links.
- Deduplication by tweet id and article id.
- Per-source metadata normalization.

### Phase 3: Local Research Corpus

- Store Markdown artifacts in a predictable folder layout.
- Add a lightweight JSONL index.
- Add summary, tags, and topic fields.
- Export JSON Feed and RSS.
- Create project libraries from the web UI.
- Maintain one `meta.md` article per project.
- Support recurring research workflows for business and AI monitoring.

### Phase 4: Official X MCP Bridge

- Optional adapter for a locally configured official X MCP server.
- Authenticated search and account-specific retrieval with user credentials.
- Same output shape: Markdown + metadata + raw source.

### Phase 5: Agent Workflows

- Codex skill commands for fetching links.
- Author and topic summarization.
- Weekly trend digests.
- Cross-topic post comparison.
- Research note export.

## Legal And Ethical Boundaries

This project is for lawful, read-only research on public URLs. It is not a scraping evasion toolkit.

Do:

- Respect X/Twitter terms, robots, rate limits, and user privacy.
- Use official APIs or your own authorized credentials when needed.
- Store full text locally for personal/research use when permitted.
- Quote sparingly and summarize long copyrighted works.

Do not:

- Bypass login, paywalls, access controls, or private accounts.
- Republish full copyrighted posts/articles without permission.
- Use the tool for spam, surveillance, harassment, or platform manipulation.
- Pretend this project is affiliated with X/Twitter.

Read [docs/LEGAL.md](docs/LEGAL.md) before using this in production.

## Extending Toward An MCP-Like Research Stack

This repo intentionally uses a simple contract:

```text
input  -> public URL / query / batch file
output -> Markdown artifact + metadata JSON + optional raw source
```

Future adapters can plug into that contract: search discovery, official X MCP integration, local corpus indexing, scheduled monitoring, and diffing.

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Disclaimer

This project is independent and is not affiliated with, endorsed by, or sponsored by X Corp. "X" and "Twitter" are mentioned only to identify compatible source URLs.
