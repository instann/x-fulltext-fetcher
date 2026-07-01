<p align="center">
  <img src="assets/hero-banner.png" alt="X Fulltext Fetcher banner" width="100%">
</p>

# X Fulltext Fetcher

> A read-only research utility and Codex skill for turning public X/Twitter links into clean Markdown notes.

X Fulltext Fetcher helps you collect public posts and X Articles for business, AI, market, and creator-research workflows. It is designed as a lightweight, MCP-like extraction layer: give it a public status URL, get back Markdown, metadata, and optional raw JSON for later indexing.

It does **not** bypass authentication, paywalls, private accounts, platform access controls, or copyright rules.

## Why This Exists

X is full of useful long-form posts and Articles, but direct pages often require login or render content through client-side data. For legitimate research, archiving your own references, and AI-assisted note-taking, this project provides a reproducible workflow:

- Fetch a public X status URL.
- Detect whether it contains an X Article.
- Convert available text blocks into Markdown.
- Preserve metadata and raw JSON when needed.
- Use the bundled Codex skill for repeatable agent workflows.

## Features

- **URL to Markdown**: Convert public `/status/<id>` links into readable Markdown.
- **X Article support**: Parse `tweet.article.content.blocks` when available.
- **Batch mode**: Process a list of links into a local corpus folder.
- **Metadata output**: Save title, source URL, tweet id, article id, block count, cover image, and API URL.
- **Raw source preservation**: Optionally store raw JSON for later auditing.
- **Codex skill included**: Installable skill for future agent-driven research workflows.
- **Extensible architecture**: Add adapters for search, official X MCP, indexing, or monitoring.

## Quick Start

```powershell
git clone <your-repo-url>
cd x-fulltext-fetcher
python scripts/fetch_x_fulltext.py "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md --metadata
```

Batch mode:

```powershell
python scripts/fetch_x_fulltext.py --batch examples/links.txt --out-dir outputs/corpus --metadata-out outputs/corpus/metadata.json --raw-json-dir outputs/raw
```

Install as a local Python package:

```powershell
python -m pip install -e .
x-fulltext-fetch "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md
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
├── assets/                       # README visuals
├── docs/
│   ├── LEGAL.md                  # compliance and acceptable use
│   ├── METHODS.md                # endpoint notes and fallback strategy
│   └── ROADMAP.md                # planned MCP-like extensions
├── examples/
│   └── links.txt                 # batch input example
├── scripts/
│   └── fetch_x_fulltext.py       # standalone CLI script
├── skills/
│   └── x-fulltext-fetcher/       # Codex skill package
├── src/
│   └── x_fulltext_fetcher/       # Python package entrypoint
└── tests/
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

Future adapters can plug into that contract:

- Search engine discovery for candidate links.
- Official X MCP integration after user credentials are configured.
- Local corpus indexing for AI and business intelligence.
- Scheduled monitoring and diffing.

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Disclaimer

This project is independent and is not affiliated with, endorsed by, or sponsored by X Corp. "X" and "Twitter" are mentioned only to identify compatible source URLs.

