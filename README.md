<p align="center">
  <img src="assets/hero-banner.png" alt="X Fulltext Fetcher banner" width="100%">
</p>

# X Fulltext Fetcher / X 全文抓取器

> EN: A read-only research utility and Codex skill for turning public X/Twitter links into clean Markdown notes.
>
> 中文：一个只读研究工具和 Codex Skill，用来把公开的 X/Twitter 链接转换成干净的 Markdown 笔记。

EN: X Fulltext Fetcher helps you collect public posts and X Articles for business, AI, market, and creator-research workflows. It works like a lightweight MCP-style extraction layer: give it a public status URL, and it returns Markdown, metadata, and optional raw JSON for later indexing.

中文：X Fulltext Fetcher 可以帮助你收集公开推文和 X Article，适合商业研究、AI 研究、市场观察、创作者内容分析等工作流。它像一个轻量级的 MCP 风格提取层：输入公开 status 链接，输出 Markdown、元数据，以及可选的原始 JSON，方便后续索引和分析。

EN: It does **not** bypass authentication, paywalls, private accounts, platform access controls, or copyright rules.

中文：它**不会**绕过登录、付费墙、私密账号、平台访问控制或版权规则。

## Why This Exists / 为什么做这个

EN: X contains many useful long-form posts and Articles, but public pages often require login or render content through client-side data. For legitimate research, personal archiving, and AI-assisted note-taking, this project provides a reproducible workflow:

中文：X 上有很多有价值的长文和 Article，但网页经常要求登录，或者通过前端动态渲染内容。为了合法研究、个人资料归档和 AI 辅助笔记，这个项目提供一个可复现的流程：

- EN: Fetch a public X status URL.
- 中文：抓取一个公开的 X status 链接。
- EN: Detect whether it contains an X Article.
- 中文：检测其中是否包含 X Article。
- EN: Convert available text blocks into Markdown.
- 中文：把可读取的文本块转换成 Markdown。
- EN: Preserve metadata and raw JSON when needed.
- 中文：按需保存元数据和原始 JSON。
- EN: Use the bundled Codex skill for repeatable agent workflows.
- 中文：通过内置 Codex Skill 支持可重复的 Agent 工作流。

## Features / 功能

- **URL to Markdown / 链接转 Markdown**: Convert public `/status/<id>` links into readable Markdown. / 将公开 `/status/<id>` 链接转换成可读 Markdown。
- **X Article support / 支持 X Article**: Parse `tweet.article.content.blocks` when available. / 在数据可用时解析 `tweet.article.content.blocks`。
- **Batch mode / 批量模式**: Process a list of links into a local corpus folder. / 将一组链接批量处理到本地语料文件夹。
- **Metadata output / 元数据输出**: Save title, source URL, tweet id, article id, block count, cover image, and API URL. / 保存标题、来源链接、tweet id、article id、块数量、封面图和 API URL。
- **Raw source preservation / 原始数据保留**: Optionally store raw JSON for later auditing. / 可选保存原始 JSON，方便之后审计。
- **Codex skill included / 内置 Codex Skill**: Installable skill for future agent-driven research workflows. / 包含可安装的 Skill，方便未来由 Agent 驱动研究流程。
- **Extensible architecture / 可扩展架构**: Add adapters for search, official X MCP, indexing, or monitoring. / 可继续接入搜索、官方 X MCP、索引或监控适配器。

## Quick Start / 快速开始

EN: Clone the repository and fetch one public X status URL:

中文：克隆仓库，并抓取一个公开 X status 链接：

```powershell
git clone https://github.com/instann/x-fulltext-fetcher.git
cd x-fulltext-fetcher
python scripts/fetch_x_fulltext.py "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md --metadata
```

EN: Batch mode:

中文：批量模式：

```powershell
python scripts/fetch_x_fulltext.py --batch examples/links.txt --out-dir outputs/corpus --metadata-out outputs/corpus/metadata.json --raw-json-dir outputs/raw
```

EN: Install as a local Python package:

中文：作为本地 Python 包安装：

```powershell
python -m pip install -e .
x-fulltext-fetch "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md
```

## Example Output / 输出示例

```markdown
# Super useful Article title

> Article preview...

Source: https://x.com/user/status/123
Article ID: 456

## Section
- Bullet
- Bullet
```

## Repository Layout / 仓库结构

```text
x-fulltext-fetcher/
|-- assets/                       # README visuals / README 视觉资源
|-- docs/
|   |-- LEGAL.md                  # compliance and acceptable use / 合规与可接受用途
|   |-- METHODS.md                # endpoint notes and fallback strategy / 端点说明与 fallback 策略
|   `-- ROADMAP.md                # planned MCP-like extensions / MCP 风格扩展计划
|-- examples/
|   `-- links.txt                 # batch input example / 批量输入示例
|-- scripts/
|   `-- fetch_x_fulltext.py       # standalone CLI script / 独立 CLI 脚本
|-- skills/
|   `-- x-fulltext-fetcher/       # Codex skill package / Codex Skill 包
|-- src/
|   `-- x_fulltext_fetcher/       # Python package entrypoint / Python 包入口
`-- tests/
```

## Codex Skill / Codex Skill

EN: The bundled skill lives in:

中文：内置 Skill 位于：

```text
skills/x-fulltext-fetcher
```

EN: To install it for Codex, copy that folder into your Codex skills directory:

中文：要安装到 Codex，请把该文件夹复制到你的 Codex skills 目录：

```powershell
Copy-Item -Recurse -Force .\skills\x-fulltext-fetcher "$env:USERPROFILE\.codex\skills\x-fulltext-fetcher"
```

EN: Then ask Codex:

中文：然后可以这样让 Codex 使用：

```text
Use $x-fulltext-fetcher to fetch and summarize this X Article link: ...
```

## How It Works / 工作原理

EN: The current primary adapter uses:

中文：当前主要适配器使用：

```text
https://api.fxtwitter.com/{screen_name}/status/{status_id}
```

EN: Observed useful fields:

中文：目前观察到的有用字段：

- `tweet.raw_text.text`
- `tweet.article.title`
- `tweet.article.preview_text`
- `tweet.article.content.blocks`
- `tweet.article.content.entityMap`
- `tweet.article.cover_media.media_info.original_img_url`

EN: See [docs/METHODS.md](docs/METHODS.md) for alternatives and limitations.

中文：替代方案和限制说明见 [docs/METHODS.md](docs/METHODS.md)。

## Update Plan / 后续更新计划

EN: The project starts as a reliable URL-to-Markdown extractor and will grow toward a small research stack.

中文：这个项目先从稳定的“链接转 Markdown”工具开始，之后会逐步扩展成一个小型研究工作台。

### Phase 1: Stable Extraction / 第一阶段：稳定提取

- EN: Public status URL support, X Article parsing, batch mode, metadata JSON, raw JSON preservation, and Codex skill packaging.
- 中文：支持公开 status 链接、X Article 解析、批量模式、元数据 JSON、原始 JSON 保存，以及 Codex Skill 打包。

### Phase 2: Discovery / 第二阶段：发现机制

- EN: Add search-engine based discovery of candidate X status links, topic watchlists, deduplication by tweet/article id, and per-source metadata normalization.
- 中文：增加基于搜索引擎的候选链接发现、主题监控列表、按 tweet/article id 去重，以及不同来源的元数据标准化。

### Phase 3: Local Research Corpus / 第三阶段：本地研究语料库

- EN: Store Markdown artifacts in a predictable folder layout, add a lightweight SQLite or JSONL index, and support summary, tags, and topic fields.
- 中文：用稳定的文件夹结构保存 Markdown，增加轻量 SQLite 或 JSONL 索引，并支持摘要、标签和主题字段。

### Phase 4: Official X MCP Bridge / 第四阶段：官方 X MCP 桥接

- EN: Add an optional adapter for a locally configured official X MCP server, supporting authenticated search and account-specific retrieval with user credentials.
- 中文：增加可选适配器，连接用户本地配置的官方 X MCP 服务，支持在用户授权凭据下进行搜索和账号相关检索。

### Phase 5: Agent Workflows / 第五阶段：Agent 工作流

- EN: Add Codex skill commands for fetching links, summarizing authors, building weekly trend digests, comparing posts across topics, and exporting research notes.
- 中文：增加更多 Codex Skill 命令，用于抓取链接、总结作者、生成每周趋势摘要、跨主题比较帖子，以及导出研究笔记。

## Legal And Ethical Boundaries / 法律与伦理边界

EN: This project is for lawful, read-only research on public URLs. It is not a scraping evasion toolkit.

中文：本项目用于对公开 URL 进行合法、只读研究。它不是绕过限制的抓取工具。

Do / 可以：

- EN: Respect X/Twitter terms, robots, rate limits, and user privacy.
- 中文：尊重 X/Twitter 条款、robots、速率限制和用户隐私。
- EN: Use official APIs or your own authorized credentials when needed.
- 中文：在需要时使用官方 API 或你自己授权的凭据。
- EN: Store full text locally for personal/research use when permitted.
- 中文：在允许的情况下，将全文保存到本地用于个人或研究用途。
- EN: Quote sparingly and summarize long copyrighted works.
- 中文：少量引用，并优先总结受版权保护的长内容。

Do not / 不可以：

- EN: Bypass login, paywalls, access controls, or private accounts.
- 中文：绕过登录、付费墙、访问控制或私密账号。
- EN: Republish full copyrighted posts/articles without permission.
- 中文：未经许可重新发布完整受版权保护的帖子或文章。
- EN: Use the tool for spam, surveillance, harassment, or platform manipulation.
- 中文：将工具用于垃圾信息、监控、骚扰或平台操纵。
- EN: Pretend this project is affiliated with X/Twitter.
- 中文：声称本项目与 X/Twitter 官方有关联。

EN: Read [docs/LEGAL.md](docs/LEGAL.md) before using this in production.

中文：在生产环境使用前，请阅读 [docs/LEGAL.md](docs/LEGAL.md)。

## Extending Toward An MCP-Like Research Stack / 向 MCP 风格研究栈扩展

EN: This repo intentionally uses a simple contract:

中文：这个仓库有意保持一个简单契约：

```text
input  -> public URL / query / batch file
output -> Markdown artifact + metadata JSON + optional raw source
```

```text
输入 -> 公开 URL / 查询 / 批量文件
输出 -> Markdown 文件 + 元数据 JSON + 可选原始数据
```

EN: Future adapters can plug into that contract: search discovery, official X MCP integration, local corpus indexing, scheduled monitoring, and diffing.

中文：未来的适配器都可以接入这个契约：搜索发现、官方 X MCP 集成、本地语料索引、定时监控和差异比较。

## Disclaimer / 免责声明

EN: This project is independent and is not affiliated with, endorsed by, or sponsored by X Corp. "X" and "Twitter" are mentioned only to identify compatible source URLs.

中文：本项目是独立项目，与 X Corp. 无从属、背书或赞助关系。文中提到 "X" 和 "Twitter" 仅用于说明兼容的来源 URL。
