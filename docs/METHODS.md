# Methods

This document records currently useful ways to retrieve readable text from public X/Twitter links.

## Primary: FXTwitter API

For a status URL:

```text
https://x.com/{screen_name}/status/{status_id}
```

call:

```text
https://api.fxtwitter.com/{screen_name}/status/{status_id}
```

Useful fields:

- `tweet.raw_text.text`: normal post text
- `tweet.article.title`: X Article title
- `tweet.article.preview_text`: Article preview
- `tweet.article.content.blocks`: Article body blocks
- `tweet.article.content.entityMap`: embedded Markdown tables, dividers, and emoji entities
- `tweet.article.cover_media.media_info.original_img_url`: cover image

This is currently the most useful unauthenticated path observed for public X Articles.

## Secondary: VXTwitter API

```text
https://api.vxtwitter.com/{screen_name}/status/{status_id}
```

Good for post metadata, cards, media, and Article preview. It may not include full Article blocks.

## Official: X oEmbed

```text
https://publish.x.com/oembed?url={encoded_status_url}&omit_script=1
```

Official and unauthenticated. Useful for embed HTML and author metadata, but usually not enough for full Article content.

## Direct X HTML

Direct `x.com` HTML can contain SSR or relay data with tweet metadata, article ids, previews, and card data. It is useful for verification but not the cleanest extraction path.

## Article-Only Links

Article-only URLs such as:

```text
https://x.com/i/article/{article_id}
https://x.com/{screen_name}/article/{article_id}
```

do not reliably expose enough data to FXTwitter. Search the article title or id to find the original `/status/{status_id}` post that shared the article.

## Official X MCP

For authenticated, account-specific, or policy-sensitive access, configure the official X MCP server separately and preserve outputs in this repository's artifact contract:

```text
Markdown + metadata JSON + optional raw JSON
```

This repo should remain read-only unless the user explicitly asks for authenticated operations.

