#!/usr/bin/env python3
"""Fetch readable text from public X/Twitter status links.

Uses FXTwitter's public API response shape and converts X Article DraftJS
blocks into Markdown. This script intentionally avoids third-party packages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

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
        "cover_image": (
            ((article.get("cover_media") or {}).get("media_info") or {}).get("original_img_url")
        ),
    }
    return "\n".join(lines).rstrip() + "\n", metadata


def fetch_one(url: str, out: str | None = None, raw_json: str | None = None) -> dict[str, Any]:
    user, status_id = parse_status_url(url)
    api_url = f"https://api.fxtwitter.com/{urllib.parse.quote(user)}/status/{status_id}"
    response = fetch_json(api_url)

    if response.get("code") not in (None, 200):
        raise SystemExit(f"FXTwitter returned code={response.get('code')}: {response.get('message')}")

    markdown, metadata = article_to_markdown(response)
    metadata["api_url"] = api_url

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch X/Twitter status or Article text as Markdown.")
    parser.add_argument("url", nargs="?", help="X/Twitter /status/<id> URL or api.fxtwitter.com status URL")
    parser.add_argument("--batch", help="Text file containing one X/Twitter status URL per line")
    parser.add_argument("--out", help="Write Markdown to this file instead of stdout; single URL mode only")
    parser.add_argument("--out-dir", help="Write batch Markdown files to this directory")
    parser.add_argument("--metadata", action="store_true", help="Print metadata JSON to stderr")
    parser.add_argument("--metadata-out", help="Write metadata JSON to this file")
    parser.add_argument("--raw-json", help="Also save the raw FXTwitter JSON response; single URL mode only")
    parser.add_argument("--raw-json-dir", help="Write raw JSON responses for batch mode")
    args = parser.parse_args()

    if args.batch:
        if args.out:
            raise SystemExit("--out is for single URL mode; use --out-dir with --batch")
        if args.raw_json:
            raise SystemExit("--raw-json is for single URL mode; use --raw-json-dir with --batch")
        out_dir = Path(args.out_dir or ".")
        urls = [
            line.strip()
            for line in Path(args.batch).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        all_metadata = []
        for url in urls:
            user, status_id = parse_status_url(url)
            stem = safe_slug(f"{user}-{status_id}")
            out_path = out_dir / f"{stem}.md"
            raw_path = None
            if args.raw_json_dir:
                raw_path = str(Path(args.raw_json_dir) / f"{stem}.json")
            metadata = fetch_one(url, out=str(out_path), raw_json=raw_path)
            all_metadata.append(metadata)
            print(str(out_path))
    else:
        if not args.url:
            raise SystemExit("Provide a URL or --batch file")
        all_metadata = [fetch_one(args.url, out=args.out, raw_json=args.raw_json)]
        if args.out:
            print(all_metadata[0]["markdown_path"])

    if args.metadata:
        print(json.dumps(all_metadata, ensure_ascii=False, indent=2), file=sys.stderr)

    if args.metadata_out:
        metadata_path = Path(args.metadata_out)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(all_metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
