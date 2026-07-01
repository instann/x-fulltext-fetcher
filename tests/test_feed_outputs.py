import json
import tempfile
import unittest
from pathlib import Path

from x_fulltext_fetcher.fetch import build_digest, load_sources, write_json_feed, write_rss_feed


class FeedOutputTest(unittest.TestCase):
    def test_load_sources_expands_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.json"
            path.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "name": "AI Operators",
                                "type": "x_status",
                                "tags": ["ai", "strategy"],
                                "urls": [
                                    "https://x.com/example/status/123",
                                    "https://x.com/example/status/456",
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            entries = load_sources(path)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["source_name"], "AI Operators")
        self.assertEqual(entries[0]["tags"], ["ai", "strategy"])

    def test_build_digest_includes_research_metadata(self):
        digest = build_digest(
            [
                {
                    "title": "Useful X Article",
                    "source_url": "https://x.com/example/status/123",
                    "kind": "article",
                    "source_name": "AI Operators",
                    "tags": ["ai"],
                    "summary": "A compact research note.",
                }
            ]
        )

        self.assertIn("# X Research Digest", digest)
        self.assertIn("Useful X Article", digest)
        self.assertIn("AI Operators", digest)

    def test_feed_writers_create_json_and_rss(self):
        items = [
            {
                "tweet_id": "123",
                "title": "Useful X Article",
                "source_url": "https://x.com/example/status/123",
                "summary": "A compact research note.",
                "tags": ["ai"],
                "fetched_at": "2026-07-02T00:00:00+00:00",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "feed.json"
            rss_path = Path(tmp) / "feed.xml"
            write_json_feed(items, json_path)
            write_rss_feed(items, rss_path)

            feed = json.loads(json_path.read_text(encoding="utf-8"))
            rss = rss_path.read_text(encoding="utf-8")

        self.assertEqual(feed["items"][0]["id"], "123")
        self.assertIn("<rss version=\"2.0\">", rss)
        self.assertIn("Useful X Article", rss)


if __name__ == "__main__":
    unittest.main()
