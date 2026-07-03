const params = new URLSearchParams(window.location.search);
const projectId = params.get("project") || "";
const markdownPath = params.get("path") || "";
const title = params.get("title") || "X 文章";

const readerTitle = document.querySelector("#readerTitle");
const markdownView = document.querySelector("#markdownView");
const rawMarkdownLink = document.querySelector("#rawMarkdownLink");

readerTitle.textContent = title;

function fileUrl() {
  return `/files/${encodeURIComponent(projectId)}/${markdownPath
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/")}`;
}

async function loadMarkdown() {
  if (!projectId || !markdownPath) {
    markdownView.innerHTML = `<p class="reader-error">缺少文章路径。</p>`;
    return;
  }
  const url = fileUrl();
  rawMarkdownLink.href = url;
  const response = await fetch(url);
  if (!response.ok) {
    markdownView.innerHTML = `<p class="reader-error">读取文章失败：HTTP ${response.status}</p>`;
    return;
  }
  const markdown = await response.text();
  const firstHeading = markdown.match(/^#\s+(.+)$/m);
  const displayMarkdown = firstHeading ? markdown.replace(firstHeading[0], "").trimStart() : markdown;
  markdownView.innerHTML = renderMarkdown(displayMarkdown);
  if (firstHeading) {
    readerTitle.textContent = firstHeading[1];
    document.title = firstHeading[1];
  }
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let paragraph = [];
  let listItems = [];
  let codeLines = [];
  let inCode = false;

  function flushParagraph() {
    if (!paragraph.length) return;
    html.push(`<p>${inline(paragraph.join(" "))}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) return;
    html.push(`<ul>${listItems.map((item) => `<li>${inline(item)}</li>`).join("")}</ul>`);
    listItems = [];
  }

  function flushCode() {
    if (!codeLines.length) return;
    html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
    codeLines = [];
  }

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.startsWith("```")) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushParagraph();
        flushList();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeLines.push(rawLine);
      continue;
    }
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length + 1;
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      flushParagraph();
      listItems.push(bullet[1]);
      continue;
    }
    if (line.startsWith("> ")) {
      flushParagraph();
      flushList();
      html.push(`<blockquote>${inline(line.slice(2))}</blockquote>`);
      continue;
    }
    if (line === "---") {
      flushParagraph();
      flushList();
      html.push("<hr>");
      continue;
    }
    paragraph.push(line);
  }
  flushParagraph();
  flushList();
  flushCode();
  return html.join("\n");
}

function inline(value) {
  return escapeHtml(value)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadMarkdown().catch((error) => {
  markdownView.innerHTML = `<p class="reader-error">${escapeHtml(error.message)}</p>`;
});
