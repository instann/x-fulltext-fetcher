---
name: x-fulltext-fetcher
description: Fetch readable text, metadata, and X Article content from public X/Twitter status links. Use when the user asks to read, extract, archive, summarize, convert to Markdown, or otherwise retrieve full text from an X/Twitter post, thread, long post, or Article URL, especially when x.com requires login or only shows previews.
---

# X Fulltext Fetcher

## Overview

Use this skill to retrieve public X/Twitter post text and X Article bodies from a link, with a reproducible fallback workflow. Treat it as a lightweight, read-only, MCP-like research tool for URL-based information collection. Prefer saving extracted full text to a local Markdown file and summarizing it in chat when the content is long or copyrighted.

## Quick Start

For a public status URL:

```powershell
python C:\Users\lgq20\.codex\skills\x-fulltext-fetcher\scripts\fetch_x_fulltext.py "https://x.com/user/status/123" --out F:\Codex\x-fulltext.md
```

The script uses `https://api.fxtwitter.com/{user}/status/{id}` and converts `tweet.article.content.blocks` into Markdown when an Article is present.

For multiple links:

```powershell
python C:\Users\lgq20\.codex\skills\x-fulltext-fetcher\scripts\fetch_x_fulltext.py --batch F:\Codex\x-links.txt --out-dir F:\Codex\x-corpus --metadata-out F:\Codex\x-corpus\metadata.json
```

## Workflow

1. Normalize the link. Prefer the original `/status/<id>` URL over `/i/article/<id>` or `/article/<id>` URLs.
2. Run `scripts/fetch_x_fulltext.py` with the URL and an `--out` path when the user wants a durable artifact.
3. If the script returns Article content, provide the file path, title, article id, block count, and a concise summary.
4. For research/corpus-building tasks, use `--raw-json`, `--raw-json-dir`, and `--metadata-out` to preserve source data for later indexing.
5. If the user needs exact local text, point them to the generated Markdown file rather than pasting a full copyrighted article into chat.
6. If the script fails, read `references/methods.md` and try the fallback methods in order.

## MCP-Like Extension Pattern

This skill is read-only by default. For authenticated X operations such as posting, account-specific search, or official API access, use the local official X MCP project if configured at `F:\Codex\xmcp`. For unauthenticated research, extend this skill by adding adapters under `scripts/` and documenting them in `references/methods.md`.

When adding capabilities, preserve this shape:

- input: URL, handle, query, or batch file
- output: Markdown artifact plus metadata JSON
- source preservation: raw JSON or source URL
- chat response: short summary, file path, and caveats

## Fallbacks

Read `references/methods.md` when:

- the link is an Article-only URL,
- `api.fxtwitter.com` returns 404 or omits `tweet.article`,
- the user asks how the method works,
- the user wants alternative services or verification.

Useful checks:

```powershell
curl.exe -L -s "https://api.fxtwitter.com/user/status/123"
curl.exe -L -s "https://api.vxtwitter.com/user/status/123"
curl.exe -L -s "https://publish.x.com/oembed?url=https%3A%2F%2Fx.com%2Fuser%2Fstatus%2F123&omit_script=1"
```

## Output Policy

Respect copyright limits in chat. For long X Articles or third-party posts, do not paste the entire article verbatim into the final answer. Instead, create a local Markdown artifact, quote only short excerpts when needed, and provide summaries, outlines, citations, and the exact command used.

## Resources

- `scripts/fetch_x_fulltext.py`: deterministic extractor for status URLs and X Article block content.
- `references/methods.md`: current endpoint notes, fallbacks, and limitations.
