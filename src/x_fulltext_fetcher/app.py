"""Local web app for collecting public X articles into project libraries."""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .fetch import fetch_one, safe_slug, utc_now

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


APP_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = APP_ROOT / "web"
PROJECTS_ROOT = APP_ROOT / "outputs" / "projects"


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler: BaseHTTPRequestHandler, text: str, status: int = 200) -> None:
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("请求体不是有效 JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("请求体必须是 JSON object")
    return data


def project_dir(project_id: str) -> Path:
    return PROJECTS_ROOT / safe_slug(project_id)


def project_json_path(project_id: str) -> Path:
    return project_dir(project_id) / "project.json"


def readable_path(path: Path) -> str:
    try:
        return str(path.relative_to(APP_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def load_project(project_id: str) -> dict[str, Any]:
    path = project_json_path(project_id)
    if not path.exists():
        raise FileNotFoundError(project_id)
    return json.loads(path.read_text(encoding="utf-8"))


def save_project(project: dict[str, Any]) -> None:
    directory = project_dir(project["id"])
    directory.mkdir(parents=True, exist_ok=True)
    project_json_path(project["id"]).write_text(
        json.dumps(project, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_meta_article(project)


def unique_project_id(name: str) -> str:
    base = safe_slug(name.lower())
    candidate = base
    index = 2
    while project_json_path(candidate).exists():
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def list_projects() -> list[dict[str, Any]]:
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    projects = []
    for path in sorted(PROJECTS_ROOT.glob("*/project.json")):
        try:
            project = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        project["article_count"] = len(project.get("articles", []))
        projects.append(project)
    return sorted(projects, key=lambda item: item.get("updated_at", ""), reverse=True)


def create_project(name: str, description: str = "") -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise ValueError("项目名称不能为空")
    now = utc_now()
    project = {
        "id": unique_project_id(name),
        "name": name,
        "description": description.strip(),
        "created_at": now,
        "updated_at": now,
        "articles": [],
        "meta_article_path": "meta.md",
    }
    save_project(project)
    return project


def write_meta_article(project: dict[str, Any]) -> None:
    directory = project_dir(project["id"])
    articles = project.get("articles", [])
    lines = [
        f"# {project.get('name', '未命名项目')}：元文章",
        "",
    ]
    if project.get("description"):
        lines.extend([f"> {project['description']}", ""])
    lines.extend(
        [
            f"- 项目 ID：`{project['id']}`",
            f"- 更新时间：{project.get('updated_at', '')}",
            f"- 收录文章：{len(articles)} 篇",
            "",
            "## 项目库摘要草稿",
            "",
            "这里会持续汇总项目库中的 X 文章。后续可以把本文交给 Agent，对所有文章做主题归纳、观点提炼、反共识发现和行动建议。",
            "",
            "## 已收录文章",
            "",
        ]
    )
    if not articles:
        lines.append("暂未收录文章。")
    for index, article in enumerate(articles, start=1):
        title = article.get("title") or "未命名文章"
        rel_path = article.get("markdown_path") or ""
        summary = article.get("summary") or ""
        source = article.get("source_url") or article.get("source") or ""
        lines.extend(
            [
                f"### {index}. [{title}]({rel_path})",
                "",
                f"- 来源：{source}",
                f"- 抓取时间：{article.get('fetched_at', '')}",
                "",
            ]
        )
        if summary:
            lines.extend([summary, ""])
    (directory / "meta.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def capture_article(project_id: str, url: str) -> dict[str, Any]:
    project = load_project(project_id)
    url = url.strip()
    if not url:
        raise ValueError("X 文章 URL 不能为空")
    directory = project_dir(project_id)
    articles_dir = directory / "articles"
    raw_dir = directory / "raw"
    timestamp = utc_now().replace(":", "").replace("+", "Z")
    temp_stem = safe_slug(f"x-{timestamp}")
    markdown_path = articles_dir / f"{temp_stem}.md"
    raw_path = raw_dir / f"{temp_stem}.json"
    metadata = fetch_one(
        url,
        out=str(markdown_path),
        raw_json=str(raw_path),
        context={
            "url": url,
            "source_name": project.get("name") or "X 项目",
            "source_type": "x_status",
            "tags": ["x", "article"],
        },
    )
    title_slug = safe_slug(f"{metadata.get('tweet_id') or ''}-{metadata.get('title') or temp_stem}")[:96]
    final_markdown = unique_path(articles_dir / f"{title_slug}.md")
    final_raw = unique_path(raw_dir / f"{title_slug}.json")
    if final_markdown != markdown_path:
        final_markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.replace(final_markdown)
    if final_raw != raw_path:
        final_raw.parent.mkdir(parents=True, exist_ok=True)
        raw_path.replace(final_raw)
    article = {
        **metadata,
        "markdown_path": str(final_markdown.relative_to(directory)).replace("\\", "/"),
        "raw_json_path": str(final_raw.relative_to(directory)).replace("\\", "/"),
    }
    project.setdefault("articles", []).append(article)
    project["updated_at"] = utc_now()
    save_project(project)
    article["project_id"] = project_id
    article["meta_article_path"] = readable_path(directory / "meta.md")
    return article


class AppHandler(BaseHTTPRequestHandler):
    server_version = "XFulltextApp/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        print("%s - - %s" % (self.address_string(), format % args))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/health":
                json_response(self, {"ok": True, "projects_root": str(PROJECTS_ROOT)})
            elif path == "/api/projects":
                json_response(self, {"projects": list_projects()})
            elif path.startswith("/api/projects/"):
                self.handle_get_project(path)
            elif path.startswith("/files/"):
                self.serve_project_file(path)
            else:
                self.serve_static(path)
        except FileNotFoundError:
            json_response(self, {"error": "未找到资源"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001 - local app should show actionable error text.
            json_response(self, {"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            data = read_json_body(self)
            if path == "/api/projects":
                project = create_project(str(data.get("name") or ""), str(data.get("description") or ""))
                json_response(self, {"project": project}, HTTPStatus.CREATED)
            elif path.startswith("/api/projects/") and path.endswith("/capture"):
                project_id = unquote(path.split("/")[3])
                article = capture_article(project_id, str(data.get("url") or ""))
                json_response(self, {"article": article}, HTTPStatus.CREATED)
            else:
                json_response(self, {"error": "未知 API"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            json_response(self, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except FileNotFoundError:
            json_response(self, {"error": "项目不存在"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            json_response(self, {"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def handle_get_project(self, path: str) -> None:
        project_id = unquote(path.split("/")[3])
        project = load_project(project_id)
        meta_path = project_dir(project_id) / "meta.md"
        project["meta_article"] = meta_path.read_text(encoding="utf-8") if meta_path.exists() else ""
        json_response(self, {"project": project})

    def serve_project_file(self, path: str) -> None:
        relative = Path(unquote(path.removeprefix("/files/")))
        target = (PROJECTS_ROOT / relative).resolve()
        if not str(target).startswith(str(PROJECTS_ROOT.resolve())) or not target.exists():
            raise FileNotFoundError(path)
        self.send_file(target)

    def serve_static(self, path: str) -> None:
        if path in ("", "/"):
            target = WEB_ROOT / "index.html"
        elif path.startswith("/web/"):
            target = (APP_ROOT / path.lstrip("/")).resolve()
        elif path.startswith("/assets/"):
            target = (APP_ROOT / path.lstrip("/")).resolve()
        else:
            target = WEB_ROOT / path.lstrip("/")
        target = target.resolve()
        if not str(target).startswith(str(APP_ROOT.resolve())) or not target.exists() or target.is_dir():
            raise FileNotFoundError(path)
        self.send_file(target)

    def send_file(self, target: Path) -> None:
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8767) -> None:
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"X Fulltext Fetcher local app: http://{host}:{port}/")
    print(f"Projects are saved under: {PROJECTS_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local app.")
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local X Fulltext Fetcher app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    run(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
