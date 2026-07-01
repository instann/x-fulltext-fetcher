const fallbackFeed = {
  title: "X Research Feed",
  items: [
    {
      id: "sample-1",
      url: "https://x.com/ambertreelet/status/2071592494245285956?s=46",
      title: "Public X research item",
      summary: "A sample item showing how collected X posts and Articles appear in the local research dashboard.",
      date_published: "2026-07-02T00:00:00+00:00",
      tags: ["ai", "operators", "strategy"]
    },
    {
      id: "sample-2",
      url: "outputs/research/digest.md",
      title: "Weekly X digest draft",
      summary: "Use the CLI to turn watched X status links into Markdown notes, JSONL index records, JSON Feed output, and RSS feed output.",
      date_published: "2026-07-02T00:00:00+00:00",
      tags: ["digest", "workflow"]
    }
  ]
};

const state = {
  feed: fallbackFeed,
  selectedId: null,
  marked: new Set(JSON.parse(localStorage.getItem("xMarkedItems") || "[]")),
  query: "",
  period: "all"
};

const els = {
  feedFile: document.querySelector("#feedFile"),
  searchInput: document.querySelector("#searchInput"),
  feedList: document.querySelector("#feedList"),
  resultCount: document.querySelector("#resultCount"),
  metricItems: document.querySelector("#metricItems"),
  metricSources: document.querySelector("#metricSources"),
  metricTags: document.querySelector("#metricTags"),
  metricMarked: document.querySelector("#metricMarked"),
  detailTitle: document.querySelector("#detailTitle"),
  detailSummary: document.querySelector("#detailSummary"),
  detailMeta: document.querySelector("#detailMeta"),
  markButton: document.querySelector("#markButton"),
  openSource: document.querySelector("#openSource")
};

function normalizeItems(feed) {
  return (feed.items || []).map((item, index) => ({
    id: String(item.id || item.url || index),
    title: item.title || "Untitled X item",
    summary: item.summary || item.content_text || "",
    url: item.url || "#",
    tags: item.tags || [],
    source: item.source_name || hostFromUrl(item.url),
    date: item.date_published || item.fetched_at || ""
  }));
}

function hostFromUrl(url) {
  try {
    return new URL(url || "https://x.com", window.location.href).hostname || "local";
  } catch {
    return "local";
  }
}

function visibleItems() {
  const query = state.query.toLowerCase();
  return normalizeItems(state.feed).filter((item) => {
    const haystack = [item.title, item.summary, item.source, item.tags.join(" ")].join(" ").toLowerCase();
    return haystack.includes(query);
  });
}

function renderMetrics(items) {
  const sources = new Set(items.map((item) => item.source));
  const tags = new Set(items.flatMap((item) => item.tags));
  els.metricItems.textContent = String(items.length);
  els.metricSources.textContent = String(sources.size);
  els.metricTags.textContent = String(tags.size);
  els.metricMarked.textContent = String(state.marked.size);
}

function renderFeed() {
  const items = visibleItems();
  renderMetrics(normalizeItems(state.feed));
  els.resultCount.textContent = `${items.length} shown`;
  els.feedList.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("article");
    empty.className = "feed-card";
    empty.innerHTML = "<div><h3>No matching items</h3><p>Adjust the search or load another JSON Feed file.</p></div>";
    els.feedList.appendChild(empty);
    return;
  }

  if (!state.selectedId) {
    state.selectedId = items[0].id;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = `feed-card${item.id === state.selectedId ? " selected" : ""}`;
    card.tabIndex = 0;
    card.innerHTML = `
      <div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.summary)}</p>
        <div class="tag-row">
          ${item.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
          ${state.marked.has(item.id) ? '<span class="tag">Marked</span>' : ""}
        </div>
      </div>
      <span class="source-chip">${escapeHtml(item.source)}</span>
    `;
    card.addEventListener("click", () => selectItem(item.id));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectItem(item.id);
      }
    });
    els.feedList.appendChild(card);
  }
  renderDetail();
}

function selectItem(id) {
  state.selectedId = id;
  renderFeed();
}

function renderDetail() {
  const item = normalizeItems(state.feed).find((entry) => entry.id === state.selectedId);
  if (!item) return;
  els.detailTitle.textContent = item.title;
  els.detailSummary.textContent = item.summary || "No summary is available for this item yet.";
  els.openSource.href = item.url || "#";
  els.markButton.textContent = state.marked.has(item.id) ? "Unmark" : "Mark for review";
  els.detailMeta.innerHTML = `
    <div class="meta-row"><span>Source</span><span>${escapeHtml(item.source)}</span></div>
    <div class="meta-row"><span>Date</span><span>${escapeHtml(item.date || "Unknown")}</span></div>
    <div class="meta-row"><span>Tags</span><span>${escapeHtml(item.tags.join(", ") || "None")}</span></div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadDefaultFeed() {
  try {
    const response = await fetch("./sample-feed.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.feed = await response.json();
  } catch {
    state.feed = fallbackFeed;
  }
  renderFeed();
}

els.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderFeed();
});

els.feedFile.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  state.feed = JSON.parse(await file.text());
  state.selectedId = null;
  renderFeed();
});

els.markButton.addEventListener("click", () => {
  if (!state.selectedId) return;
  if (state.marked.has(state.selectedId)) {
    state.marked.delete(state.selectedId);
  } else {
    state.marked.add(state.selectedId);
  }
  localStorage.setItem("xMarkedItems", JSON.stringify([...state.marked]));
  renderFeed();
});

document.querySelectorAll(".segmented button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".segmented button").forEach((item) => item.classList.remove("selected"));
    button.classList.add("selected");
    state.period = button.dataset.period;
  });
});

loadDefaultFeed();
