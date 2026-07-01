# X Fulltext Fetch Methods

Use these methods in order.

## 1. FXTwitter API

For status URLs:

```text
https://api.fxtwitter.com/{screen_name}/status/{status_id}
```

Useful fields:

- `tweet.raw_text.text`: normal post text
- `tweet.article.title`: X Article title
- `tweet.article.preview_text`: X Article preview
- `tweet.article.content.blocks`: Article body blocks
- `tweet.article.content.entityMap`: embedded Markdown tables, dividers, emoji entities
- `tweet.article.cover_media.media_info.original_img_url`: cover image

This is the best public method currently observed for X Articles because it can expose `tweet.article.content.blocks`.

## 2. VXTwitter API

```text
https://api.vxtwitter.com/{screen_name}/status/{status_id}
```

Usually reliable for post metadata, cards, media, and Article title/preview. It may not include full Article body content.

## 3. X oEmbed

```text
https://publish.x.com/oembed?url={encoded_status_url}&omit_script=1
```

Official and unauthenticated. Good for author metadata and embed HTML, but it usually does not include full Article bodies.

## 4. Direct x.com HTML

Fetching the status page with a normal browser user-agent may include SSR data such as `window.__INITIAL_DATA__`, relay records, `tweet_result_by_rest_id`, `article_results`, title, preview text, and `article_id`. This can confirm that a post has an Article, but extracting the body is harder than using FXTwitter.

## 5. Article-only URLs

Article-only links like:

```text
https://x.com/i/article/{article_id}
https://x.com/{user}/article/{article_id}
```

do not reliably work with FXTwitter. Search the web for the article id or title to find the sharing `/status/{status_id}` URL, then use the status URL.

## 6. Mirrors and readers

Nitter-style mirrors, xcancel, thread readers, x-thread.org, and similar services may help with normal posts or threads. They are volatile and often fail for X Articles. Treat them as optional fallbacks, not primary infrastructure.

## Extension ideas

Keep future additions read-only unless the user explicitly asks for authenticated official API operations.

- `fetch_x_fulltext.py`: URL-to-Markdown extraction for status links and Articles.
- Future `search_x_links.py`: query a search engine or official X API, collect candidate status URLs, then pass them to `fetch_x_fulltext.py --batch`.
- Future `build_x_corpus.py`: normalize multiple Markdown/metadata outputs into a local research corpus for AI/business monitoring.
- Future official-X bridge: call the local `F:\Codex\xmcp` server after the user configures X API credentials, then store results in the same Markdown-plus-metadata shape.

## Chat output boundary

If the extracted content is long or copyrighted, write the full text to a local file and provide a summary, outline, and source links in chat. Avoid pasting the full article into the conversation.
