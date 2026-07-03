import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from x_fulltext_fetcher import app


class LocalAppTest(unittest.TestCase):
    def test_create_project_writes_meta_article(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(app, "PROJECTS_ROOT", Path(tmp)):
                project = app.create_project("AI 产品库", "研究 X 上的 AI 产品文章")
                loaded = app.load_project(project["id"])
                meta = (Path(tmp) / project["id"] / "meta.md").read_text(encoding="utf-8")

        self.assertEqual(loaded["name"], "AI 产品库")
        self.assertIn("AI 产品库：元文章", meta)
        self.assertIn("暂未收录文章", meta)

    def test_capture_article_updates_project_and_meta(self):
        def fake_fetch_one(url, out=None, raw_json=None, context=None):
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            Path(out).write_text("# 抓取结果\n\n正文", encoding="utf-8")
            Path(raw_json).parent.mkdir(parents=True, exist_ok=True)
            Path(raw_json).write_text(json.dumps({"ok": True}), encoding="utf-8")
            return {
                "kind": "article",
                "title": "值得收藏的 X 长文",
                "tweet_id": "123",
                "source_url": url,
                "summary": "这是一段摘要。",
                "fetched_at": "2026-07-03T00:00:00+00:00",
            }

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(app, "PROJECTS_ROOT", Path(tmp)), patch.object(app, "fetch_one", fake_fetch_one):
                project = app.create_project("增长案例", "")
                article = app.capture_article(project["id"], "https://x.com/example/status/123")
                loaded = app.load_project(project["id"])
                meta = (Path(tmp) / project["id"] / "meta.md").read_text(encoding="utf-8")

        self.assertEqual(article["title"], "值得收藏的 X 长文")
        self.assertEqual(len(loaded["articles"]), 1)
        self.assertIn("值得收藏的 X 长文", meta)
        self.assertIn("这是一段摘要。", meta)


if __name__ == "__main__":
    unittest.main()
