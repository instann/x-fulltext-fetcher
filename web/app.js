const state = {
  projects: [],
  activeProjectId: null,
  activeProject: null,
  busy: false
};

const els = {
  projectForm: document.querySelector("#projectForm"),
  projectName: document.querySelector("#projectName"),
  projectDescription: document.querySelector("#projectDescription"),
  projectList: document.querySelector("#projectList"),
  projectCount: document.querySelector("#projectCount"),
  activeProjectName: document.querySelector("#activeProjectName"),
  activeProjectDescription: document.querySelector("#activeProjectDescription"),
  saveLocation: document.querySelector("#saveLocation"),
  captureForm: document.querySelector("#captureForm"),
  articleUrl: document.querySelector("#articleUrl"),
  captureButton: document.querySelector("#captureButton"),
  statusLine: document.querySelector("#statusLine"),
  articleList: document.querySelector("#articleList"),
  articleCount: document.querySelector("#articleCount"),
  metaPreview: document.querySelector("#metaPreview"),
  metaFileLink: document.querySelector("#metaFileLink")
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function setStatus(message, tone = "muted") {
  els.statusLine.textContent = message;
  els.statusLine.dataset.tone = tone;
}

async function loadProjects() {
  const data = await api("/api/projects");
  state.projects = data.projects || [];
  if (!state.activeProjectId && state.projects.length) {
    state.activeProjectId = state.projects[0].id;
  }
  renderProjects();
  if (state.activeProjectId) {
    await loadProject(state.activeProjectId);
  } else {
    renderEmptyProject();
  }
}

async function loadProject(projectId) {
  const data = await api(`/api/projects/${encodeURIComponent(projectId)}`);
  state.activeProject = data.project;
  state.activeProjectId = data.project.id;
  renderProjects();
  renderActiveProject();
}

function renderProjects() {
  els.projectCount.textContent = `${state.projects.length} 个`;
  els.projectList.innerHTML = "";
  if (!state.projects.length) {
    els.projectList.innerHTML = `<div class="empty">还没有项目。先在上方创建一个研究项目。</div>`;
    return;
  }
  for (const project of state.projects) {
    const button = document.createElement("button");
    button.className = `project-item${project.id === state.activeProjectId ? " active" : ""}`;
    button.type = "button";
    button.innerHTML = `
      <span class="project-name">${escapeHtml(project.name)}</span>
      <span class="project-meta">${project.article_count || project.articles?.length || 0} 篇文章 · ${escapeHtml(formatDate(project.updated_at))}</span>
    `;
    button.addEventListener("click", () => loadProject(project.id));
    els.projectList.appendChild(button);
  }
}

function renderEmptyProject() {
  els.activeProjectName.textContent = "请先创建或选择项目";
  els.activeProjectDescription.textContent = "项目中的文章会保存为 Markdown，元文章会自动更新。";
  els.saveLocation.textContent = "outputs/projects";
  els.articleCount.textContent = "0 篇";
  els.articleList.innerHTML = `<div class="empty">还没有文章。选择项目后，粘贴 X status URL 开始收录。</div>`;
  els.metaPreview.textContent = "选择项目后，这里会显示项目元文章。";
  els.metaFileLink.href = "#";
}

function renderActiveProject() {
  const project = state.activeProject;
  if (!project) return renderEmptyProject();
  const articles = project.articles || [];
  els.activeProjectName.textContent = project.name;
  els.activeProjectDescription.textContent = project.description || "这个项目暂时还没有说明。";
  els.saveLocation.textContent = `outputs/projects/${project.id}`;
  els.articleCount.textContent = `${articles.length} 篇`;
  els.metaPreview.textContent = project.meta_article || "meta.md 暂无内容。";
  els.metaFileLink.href = `/files/${encodeURIComponent(project.id)}/meta.md`;
  renderArticles(articles, project.id);
}

function renderArticles(articles, projectId) {
  els.articleList.innerHTML = "";
  if (!articles.length) {
    els.articleList.innerHTML = `<div class="empty">这个项目还没有收录文章。把 X 链接粘贴到上方即可抓取。</div>`;
    return;
  }
  for (const article of [...articles].reverse()) {
    const item = document.createElement("article");
    item.className = "article-card";
    const markdownHref = `/files/${encodeURIComponent(projectId)}/${encodePath(article.markdown_path || "")}`;
    const readerHref = `/reader.html?project=${encodeURIComponent(projectId)}&path=${encodeURIComponent(article.markdown_path || "")}&title=${encodeURIComponent(article.title || "未命名文章")}`;
    item.innerHTML = `
      <div>
        <h3><a href="${escapeHtml(readerHref)}">${escapeHtml(article.title || "未命名文章")}</a></h3>
        <p>${escapeHtml(article.summary || "暂无摘要。")}</p>
        <div class="article-meta">
          <span>${escapeHtml(article.kind || "article")}</span>
          <span>${escapeHtml(formatDate(article.fetched_at))}</span>
        </div>
      </div>
      <div class="article-actions">
        <a href="${escapeHtml(readerHref)}">阅读</a>
        <a href="${escapeHtml(article.source_url || article.source || "#")}" target="_blank" rel="noreferrer">原文</a>
      </div>
    `;
    item.addEventListener("click", (event) => {
      if (event.target.closest("a")) return;
      window.location.href = readerHref;
    });
    els.articleList.appendChild(item);
  }
}

els.projectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    setStatus("正在创建项目...");
    const data = await api("/api/projects", {
      method: "POST",
      body: JSON.stringify({
        name: els.projectName.value,
        description: els.projectDescription.value
      })
    });
    els.projectForm.reset();
    state.activeProjectId = data.project.id;
    await loadProjects();
    setStatus("项目已创建，可以开始收录 X 文章。", "ok");
  } catch (error) {
    setStatus(error.message, "error");
  }
});

els.captureForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.activeProjectId) {
    setStatus("请先创建或选择一个项目。", "error");
    return;
  }
  if (state.busy) return;
  state.busy = true;
  els.captureButton.disabled = true;
  els.captureButton.textContent = "抓取中...";
  try {
    setStatus("正在抓取 X 文章并保存到本地，请稍等...");
    await api(`/api/projects/${encodeURIComponent(state.activeProjectId)}/capture`, {
      method: "POST",
      body: JSON.stringify({ url: els.articleUrl.value })
    });
    els.articleUrl.value = "";
    await loadProjects();
    setStatus("已收录文章，并更新项目元文章。", "ok");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    state.busy = false;
    els.captureButton.disabled = false;
    els.captureButton.textContent = "抓取并收录";
  }
});

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function encodePath(path) {
  return String(path || "")
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
}

function formatDate(value) {
  if (!value) return "刚刚";
  try {
    return new Intl.DateTimeFormat("zh-CN", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    }).format(new Date(value));
  } catch {
    return value;
  }
}

loadProjects().catch((error) => {
  setStatus(`本地应用未就绪：${error.message}`, "error");
  renderEmptyProject();
});
