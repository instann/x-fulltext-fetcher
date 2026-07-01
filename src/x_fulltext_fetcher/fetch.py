#!/usr/bin/env python3
"""Fetch readable text from public X/Twitter status links.

Uses FXTwitter's public API response shape and converts X Article DraftJS
blocks into Markdown. This script intentionally avoids third-party packages.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


STATUS_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/([^/?#]+)/status/(\d+)", re.I)
FX_RE = re.compile(r"https?://api\.fxtwitter\.com/([^/?#]+)/status/(\d+)", re.I)
ARTICLE_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/(?:i/)?article/(\d+)", re.I)


def parse_status_url(url: str) -> tuple[str, str]:
    for pattern in (STATUS_RE, FX_RE):
        match = pattern.search(url)
        if match:
            return match.group(1), match.group(2)

    article_match = ARTICLE_RE.search(url)
    if article_match:
        raise SystemExit(
            "Article-only URLs do not expose enough information for FXTwitter. "
            "Find the original /status/<id> post that shared this article, then retry. "
            f"Article id: {article_match.group(1)}"
        )

    raise SystemExit("Expected a URL like https://x.com/user/status/123")


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} from {url}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not fetch {url}: {exc.reason}") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Response was not JSON: {payload[:500]}") from exc


def entity_map_to_dict(entity_map: Any) -> dict[str, Any]:
    if isinstance(entity_map, dict):
        return {str(key): value for key, value in entity_map.items()}

    result: dict[str, Any] = {}
    if isinstance(entity_map, list):
        for item in entity_map:
            if isinstance(item, dict) and "key" in item and "value" in item:
                result[str(item["key"])] = item["value"]
    return result


def safe_slug(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")
    return slug or "x-content"


def compact_text(text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_batch_urls(path: str | Path) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def load_sources(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = data.get("sources", data if isinstance(data, list) else [])
    if not isinstance(sources, list):
        raise SystemExit("Sources file must contain a list or a top-level 'sources' list")

    entries: list[dict[str, Any]] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        name = str(source.get("name") or "X Source")
        tags = [str(tag) for tag in source.get("tags", []) if str(tag).strip()]
        urls = source.get("urls") or []
        if source.get("url"):
            urls = [source["url"], *urls]
        for url in urls:
            if not str(url).strip():
                continue
            entries.append(
                {
                    "source_name": name,
                    "source_type": str(source.get("type") or "x_status"),
                    "url": str(url).strip(),
                    "tags": tags,
                    "note": str(source.get("note") or "").strip(),
                }
            )
    return entries


def atomic_markdown(block: dict[str, Any], entities: dict[str, Any]) -> str:
    for item in block.get("entityRanges") or []:
        key = str(item.get("key"))
        entity = entities.get(key)
        if not isinstance(entity, dict):
            continue
        entity_type = entity.get("type")
        data = entity.get("data") or {}
        if entity_type == "MARKDOWN":
            return "\n" + str(data.get("markdown", "")).strip() + "\n"
        if entity_type == "DIVIDER":
            return "\n---\n"
    return ""


def article_to_markdown(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    tweet = response.get("tweet") or {}
    article = tweet.get("article")
    if not article:
        text = (
            tweet.get("raw_text", {}).get("text")
            or tweet.get("text")
            or ""
        )
        title = f"X post {tweet.get('id', '')}".strip()
        lines = [f"# {title}", "", text]
        return "\n".join(line for line in lines if line is not None), {
            "kind": "post",
            "title": title,
            "tweet_id": tweet.get("id"),
            "block_count": 0,
            "summary": compact_text(text),
            "source": tweet.get("url"),
        }

    content = article.get("content") or {}
    blocks = content.get("blocks") or []
    entities = entity_map_to_dict(content.get("entityMap"))

    title = article.get("title") or f"X Article {article.get('id', '')}".strip()
    lines: list[str] = [
        f"# {title}",
        "",
    ]
    preview = article.get("preview_text")
    if preview:
        lines.extend([f"> {preview}", ""])
    if tweet.get("url"):
        lines.append(f"Source: {tweet['url']}")
    if article.get("id"):
        lines.append(f"Article ID: {article['id']}")
    lines.append("")

    for block in blocks:
        if not isinstance(block, dict):
            continue
        text = str(block.get("text") or "")
        stripped = text.strip()
        block_type = block.get("type")

        if block_type == "header-one" and stripped:
            lines.append(f"# {text}")
        elif block_type == "header-two" and stripped:
            lines.append(f"## {text}")
        elif block_type == "header-three" and stripped:
            lines.append(f"### {text}")
        elif block_type == "unordered-list-item" and stripped:
            lines.append(f"- {text}")
        elif block_type == "ordered-list-item" and stripped:
            lines.append(f"1. {text}")
        elif block_type == "blockquote" and stripped:
            lines.append(f"> {text}")
        elif block_type == "atomic":
            rendered = atomic_markdown(block, entities).strip()
            if rendered:
                lines.append(rendered)
        elif stripped:
            lines.append(text)

    metadata = {
        "kind": "article",
        "title": title,
        "tweet_id": tweet.get("id"),
        "article_id": article.get("id"),
        "block_count": len(blocks),
        "source": tweet.get("url"),
        "summary": compact_text(preview or "\n".join(lines)),
        "cover_image": (
            ((article.get("cover_media") or {}).get("media_info") or {}).get("original_img_url")
        ),
    }
    return "\n".join(lines).rstrip() + "\n", metadata


def enrich_metadata(metadata: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    result = dict(metadata)
    result.setdefault("source_url", context.get("url") or result.get("source"))
    result.setdefault("source_name", context.get("source_name") or "X")
    result.setdefault("source_type", context.get("source_type") or "x_status")
    result.setdefault("tags", context.get("tags") or [])
    result.setdefault("note", context.get("note") or "")
    result.setdefault("fetched_at", utc_now())
    return result


def fetch_one(
    url: str,
    out: str | None = None,
    raw_json: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    user, status_id = parse_status_url(url)
    api_url = f"https://api.fxtwitter.com/{urllib.parse.quote(user)}/status/{status_id}"
    response = fetch_json(api_url)

    if response.get("code") not in (None, 200):
        raise SystemExit(f"FXTwitter returned code={response.get('code')}: {response.get('message')}")

    markdown, metadata = article_to_markdown(response)
    metadata["api_url"] = api_url
    metadata = enrich_metadata(metadata, context or {"url": url})

    if raw_json:
        raw_json_path = Path(raw_json)
        raw_json_path.parent.mkdir(parents=True, exist_ok=True)
        raw_json_path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
        metadata["raw_json_path"] = str(raw_json_path)

    if out:
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        metadata["markdown_path"] = str(output_path)
    else:
        sys.stdout.write(markdown)

    return metadata


def write_jsonl(items: list[dict[str, Any]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in items) + "\n",
        encoding="utf-8",
    )


def build_digest(items: list[dict[str, Any]], title: str = "X Research Digest") -> str:
    generated_at = utc_now()
    lines = [
        f"# {title}",
        "",
        f"Generated: {generated_at}",
        f"Items: {len(items)}",
        "",
    ]
    for item in items:
        heading = item.get("title") or item.get("tweet_id") or "Untitled X item"
        lines.extend(
            [
                f"## {heading}",
                "",
                f"- Source: {item.get('source_url') or item.get('source') or ''}",
                f"- Type: {item.get('kind') or 'post'}",
                f"- Collection: {item.get('source_name') or 'X'}",
            ]
        )
        tags = item.get("tags") or []
        if tags:
            lines.append(f"- Tags: {', '.join(str(tag) for tag in tags)}")
        if item.get("summary"):
            lines.extend(["", str(item["summary"])])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_json_feed(items: list[dict[str, Any]], path: str | Path, title: str = "X Research Feed") -> None:
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": title,
        "home_page_url": "https://github.com/instann/x-fulltext-fetcher",
        "feed_url": "feed.json",
        "items": [
            {
                "id": str(item.get("tweet_id") or item.get("article_id") or item.get("source_url")),
                "url": item.get("source_url") or item.get("source"),
                "title": item.get("title") or "X item",
                "summary": item.get("summary") or "",
                "content_text": item.get("summary") or item.get("title") or "",
                "date_published": item.get("fetched_at"),
                "tags": item.get("tags") or [],
            }
            for item in items
        ],
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")


def write_rss_feed(items: list[dict[str, Any]], path: str | Path, title: str = "X Research Feed") -> None:
    item_xml = []
    for item in items:
        link = item.get("source_url") or item.get("source") or ""
        description = html.escape(str(item.get("summary") or ""))
        item_xml.append(
            "\n".join(
                [
                    "    <item>",
                    f"      <title>{escape(str(item.get('title') or 'X item'))}</title>",
                    f"      <link>{escape(str(link))}</link>",
                    f"      <guid>{escape(str(item.get('tweet_id') or item.get('article_id') or link))}</guid>",
                    f"      <description>{description}</description>",
                    "    </item>",
                ]
            )
        )
    xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            f"    <title>{escape(title)}</title>",
            "    <link>https://github.com/instann/x-fulltext-fetcher</link>",
            "    <description>Curated X research feed</description>",
            *item_xml,
            "  </channel>",
            "</rss>",
            "",
        ]
    )
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")


def process_entries(
    entries: list[dict[str, Any]],
    out_dir: Path,
    raw_json_dir: Path | None = None,
) -> list[dict[str, Any]]:
    all_metadata = []
    for entry in entries:
        user, status_id = parse_status_url(entry["url"])
        stem = safe_slug(f"{entry.get('source_name', user)}-{user}-{status_id}")
        out_path = out_dir / f"{stem}.md"
        raw_path = None
        if raw_json_dir:
            raw_path = str(raw_json_dir / f"{stem}.json")
        metadata = fetch_one(entry["url"], out=str(out_path), raw_json=raw_path, context=entry)
        all_metadata.append(metadata)
        print(str(out_path))
    return all_metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch X/Twitter status or Article text as Markdown.")
    parser.add_argument("url", nargs="?", help="X/Twitter /status/<id> URL or api.fxtwitter.com status URL")
    parser.add_argument("--batch", help="Text file containing one X/Twitter status URL per line")
    parser.add_argument("--sources", help="JSON source configuration for X research feeds")
    parser.add_argument("--out", help="Write Markdown to this file instead of stdout; single URL mode only")
    parser.add_argument("--out-dir", help="Write batch Markdown files to this directory")
    parser.add_argument("--digest-out", help="Write a Markdown digest for batch or sources mode")
    parser.add_argument("--index-out", help="Write JSONL metadata index for batch or sources mode")
    parser.add_argument("--feed-json", help="Write JSON Feed output for batch or sources mode")
    parser.add_argument("--feed-rss", help="Write RSS output for batch or sources mode")
    parser.add_argument("--metadata", action="store_true", help="Print metadata JSON to stderr")
    parser.add_argument("--metadata-out", help="Write metadata JSON to this file")
    parser.add_argument("--raw-json", help="Also save the raw FXTwitter JSON response; single URL mode only")
    parser.add_argument("--raw-json-dir", help="Write raw JSON responses for batch mode")
    args = parser.parse_args()

    if args.batch or args.sources:
        if args.out:
            raise SystemExit("--out is for single URL mode; use --out-dir with --batch or --sources")
        if args.raw_json:
            raise SystemExit("--raw-json is for single URL mode; use --raw-json-dir with --batch or --sources")
        out_dir = Path(args.out_dir or ".")
        entries = []
        if args.batch:
            entries.extend({"url": url} for url in read_batch_urls(args.batch))
        if args.sources:
            entries.extend(load_sources(args.sources))
        all_metadata = process_entries(entries, out_dir, Path(args.raw_json_dir) if args.raw_json_dir else None)
    else:
        if not args.url:
            raise SystemExit("Provide a URL, --batch file, or --sources file")
        all_metadata = [fetch_one(args.url, out=args.out, raw_json=args.raw_json)]
        if args.out:
            print(all_metadata[0]["markdown_path"])

    if args.digest_out:
        digest_path = Path(args.digest_out)
        digest_path.parent.mkdir(parents=True, exist_ok=True)
        digest_path.write_text(build_digest(all_metadata), encoding="utf-8")

    if args.index_out:
        write_jsonl(all_metadata, args.index_out)

    if args.feed_json:
        write_json_feed(all_metadata, args.feed_json)

    if args.feed_rss:
        write_rss_feed(all_metadata, args.feed_rss)

    if args.metadata:
        print(json.dumps(all_metadata, ensure_ascii=False, indent=2), file=sys.stderr)

    if args.metadata_out:
        metadata_path = Path(args.metadata_out)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(all_metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
