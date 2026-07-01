<p align="center">
  <img src="assets/hero-banner.png" alt="X Fulltext Fetcher banner" width="100%">
</p>

<p align="center">
  <a href="./README.md">English</a> / <strong>简体中文</strong>
</p>

# X 全文抓取器

> 一个只读研究工具和 Codex Skill，用来把公开的 X/Twitter 链接转换成干净的 Markdown 笔记。

X 全文抓取器可以帮助你收集公开推文和 X Article，适合商业研究、AI 研究、市场观察、创作者内容分析等工作流。它像一个轻量级的 MCP 风格提取层：输入公开 status 链接，输出 Markdown、元数据，以及可选的原始 JSON，方便后续索引和分析。

它**不会**绕过登录、付费墙、私密账号、平台访问控制或版权规则。

## 为什么做这个

X 上有很多有价值的长文和 Article，但网页经常要求登录，或者通过前端动态渲染内容。为了合法研究、个人资料归档和 AI 辅助笔记，这个项目提供一个可复现的流程：

- 抓取一个公开的 X status 链接。
- 检测其中是否包含 X Article。
- 把可读取的文本块转换成 Markdown。
- 按需保存元数据和原始 JSON。
- 通过内置 Codex Skill 支持可重复的 Agent 工作流。

## 功能

- **链接转 Markdown**：将公开 `/status/<id>` 链接转换成可读 Markdown。
- **支持 X Article**：在数据可用时解析 `tweet.article.content.blocks`。
- **批量模式**：将一组链接批量处理到本地语料文件夹。
- **元数据输出**：保存标题、来源链接、tweet id、article id、块数量、封面图和 API URL。
- **原始数据保留**：可选保存原始 JSON，方便之后审计。
- **内置 Codex Skill**：包含可安装的 Skill，方便未来由 Agent 驱动研究流程。
- **可扩展架构**：可继续接入搜索、官方 X MCP、索引或监控适配器。

## 快速开始

克隆仓库，并抓取一个公开 X status 链接：

```powershell
git clone https://github.com/instann/x-fulltext-fetcher.git
cd x-fulltext-fetcher
python scripts/fetch_x_fulltext.py "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md --metadata
```

批量模式：

```powershell
python scripts/fetch_x_fulltext.py --batch examples/links.txt --out-dir outputs/corpus --metadata-out outputs/corpus/metadata.json --raw-json-dir outputs/raw
```

作为本地 Python 包安装：

```powershell
python -m pip install -e .
x-fulltext-fetch "https://x.com/ambertreelet/status/2071592494245285956?s=46" --out outputs/article.md
```

## 输出示例

```markdown
# Super useful Article title

> Article preview...

Source: https://x.com/user/status/123
Article ID: 456

## Section
- Bullet
- Bullet
```

## 仓库结构

```text
x-fulltext-fetcher/
|-- assets/                       # README 视觉资源
|-- docs/
|   |-- LEGAL.md                  # 合规与可接受用途
|   |-- METHODS.md                # 端点说明与 fallback 策略
|   `-- ROADMAP.md                # MCP 风格扩展计划
|-- examples/
|   `-- links.txt                 # 批量输入示例
|-- scripts/
|   `-- fetch_x_fulltext.py       # 独立 CLI 脚本
|-- skills/
|   `-- x-fulltext-fetcher/       # Codex Skill 包
|-- src/
|   `-- x_fulltext_fetcher/       # Python 包入口
`-- tests/
```

## Codex Skill

内置 Skill 位于：

```text
skills/x-fulltext-fetcher
```

要安装到 Codex，请把该文件夹复制到你的 Codex skills 目录：

```powershell
Copy-Item -Recurse -Force .\skills\x-fulltext-fetcher "$env:USERPROFILE\.codex\skills\x-fulltext-fetcher"
```

然后可以这样让 Codex 使用：

```text
Use $x-fulltext-fetcher to fetch and summarize this X Article link: ...
```

## 工作原理

当前主要适配器使用：

```text
https://api.fxtwitter.com/{screen_name}/status/{status_id}
```

目前观察到的有用字段：

- `tweet.raw_text.text`
- `tweet.article.title`
- `tweet.article.preview_text`
- `tweet.article.content.blocks`
- `tweet.article.content.entityMap`
- `tweet.article.cover_media.media_info.original_img_url`

替代方案和限制说明见 [docs/METHODS.md](docs/METHODS.md)。

## 后续更新计划

这个项目先从稳定的“链接转 Markdown”工具开始，之后会逐步扩展成一个小型研究工作台。

### 第一阶段：稳定提取

- 支持公开 status 链接。
- 解析 X Article 内容块。
- 支持批量模式。
- 输出元数据 JSON。
- 保存原始 JSON。
- 打包 Codex Skill。

### 第二阶段：发现机制

- 基于搜索引擎发现候选 X status 链接。
- 增加域名和主题监控列表。
- 按 tweet id 和 article id 去重。
- 标准化不同来源的元数据。

### 第三阶段：本地研究语料库

- 用稳定的文件夹结构保存 Markdown。
- 增加轻量 SQLite 或 JSONL 索引。
- 增加摘要、标签和主题字段。
- 支持商业与 AI 监控中的周期性研究流程。

### 第四阶段：官方 X MCP 桥接

- 增加可选适配器，连接用户本地配置的官方 X MCP 服务。
- 在用户授权凭据下支持搜索和账号相关检索。
- 保持同样的输出形态：Markdown + 元数据 + 原始数据。

### 第五阶段：Agent 工作流

- 增加抓取链接的 Codex Skill 命令。
- 支持作者和主题总结。
- 生成每周趋势摘要。
- 跨主题比较帖子。
- 导出研究笔记。

## 法律与伦理边界

本项目用于对公开 URL 进行合法、只读研究。它不是绕过限制的抓取工具。

可以：

- 尊重 X/Twitter 条款、robots、速率限制和用户隐私。
- 在需要时使用官方 API 或你自己授权的凭据。
- 在允许的情况下，将全文保存到本地用于个人或研究用途。
- 少量引用，并优先总结受版权保护的长内容。

不可以：

- 绕过登录、付费墙、访问控制或私密账号。
- 未经许可重新发布完整受版权保护的帖子或文章。
- 将工具用于垃圾信息、监控、骚扰或平台操纵。
- 声称本项目与 X/Twitter 官方有关联。

在生产环境使用前，请阅读 [docs/LEGAL.md](docs/LEGAL.md)。

## 向 MCP 风格研究栈扩展

这个仓库有意保持一个简单契约：

```text
输入 -> 公开 URL / 查询 / 批量文件
输出 -> Markdown 文件 + 元数据 JSON + 可选原始数据
```

未来的适配器都可以接入这个契约：搜索发现、官方 X MCP 集成、本地语料索引、定时监控和差异比较。

更多计划见 [docs/ROADMAP.md](docs/ROADMAP.md)。

## 免责声明

本项目是独立项目，与 X Corp. 无从属、背书或赞助关系。文中提到 "X" 和 "Twitter" 仅用于说明兼容的来源 URL。
