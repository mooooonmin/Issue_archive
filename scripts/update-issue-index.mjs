import fs from "node:fs";
import process from "node:process";

const token = process.env.GITHUB_TOKEN;
const repo = process.env.GITHUB_REPOSITORY;
const readmePath = process.env.README_PATH || "README.md";

if (!token) {
  throw new Error("GITHUB_TOKEN is required.");
}
if (!repo || !repo.includes("/")) {
  throw new Error("GITHUB_REPOSITORY must look like owner/repo.");
}

const [owner, repoName] = repo.split("/");

async function fetchIssues() {
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "issue-index-updater",
  };

  let page = 1;
  const all = [];

  while (true) {
    const url = new URL(
      `https://api.github.com/repos/${owner}/${repoName}/issues`
    );
    url.searchParams.set("state", "all");
    url.searchParams.set("per_page", "100");
    url.searchParams.set("page", String(page));
    url.searchParams.set("sort", "created");
    url.searchParams.set("direction", "desc");

    const res = await fetch(url, { headers });
    if (!res.ok) {
      const msg = await res.text();
      throw new Error(`GitHub API error (${res.status}): ${msg}`);
    }

    const data = await res.json();
    const onlyIssues = data.filter((item) => !item.pull_request);
    all.push(...onlyIssues);

    if (data.length < 100) {
      break;
    }
    page += 1;
  }

  return all;
}

function toKstIso(date = new Date()) {
  return date.toLocaleString("sv-SE", {
    timeZone: "Asia/Seoul",
    hour12: false,
  });
}

const UNLABELED = "미분류";

function issueLine(issue) {
  const title = String(issue.title || "").replace(/\r?\n/g, " ").trim();
  const open = issue.state === "open" ? " _(open)_" : "";
  return `- [#${issue.number}](${issue.html_url}) ${title}${open}`;
}

// Same rule GitHub uses for heading anchors.
function anchor(heading) {
  return heading
    .toLowerCase()
    .replace(/[^\p{L}\p{N} _-]/gu, "")
    .replace(/ /g, "-");
}

// An issue with several labels is listed under each of them.
function groupByLabel(issues) {
  const groups = new Map();
  for (const issue of issues) {
    const names = (issue.labels || []).map((l) => l.name);
    for (const name of names.length ? names : [UNLABELED]) {
      if (!groups.has(name)) groups.set(name, []);
      groups.get(name).push(issue);
    }
  }
  // Most issues first; 미분류 always last.
  return [...groups.entries()].sort(([a, x], [b, y]) => {
    if (a === UNLABELED) return 1;
    if (b === UNLABELED) return -1;
    return y.length - x.length || a.localeCompare(b);
  });
}

function labelSearchUrl(name) {
  const q = encodeURIComponent(`is:issue label:"${name}"`);
  return `https://github.com/${owner}/${repoName}/issues?q=${q}`;
}

function buildIndex(issues) {
  const groups = groupByLabel(issues);
  const headings = groups.map(([name, list]) => `${name} (${list.length})`);

  const lines = [];
  lines.push("## Issue Index");
  lines.push("");
  lines.push(
    `업데이트: ${toKstIso()} (KST) / 총 ${issues.length}개`
  );
  lines.push("");

  if (groups.length === 0) {
    lines.push("- 없음");
    return lines.join("\n");
  }

  lines.push(headings.map((h) => `[${h}](#${anchor(h)})`).join(" · "));

  groups.forEach(([name, list], i) => {
    lines.push("");
    lines.push(`### ${headings[i]}`);
    if (name !== UNLABELED) {
      lines.push("");
      lines.push(`[이슈 목록에서 보기](${labelSearchUrl(name)})`);
    }
    lines.push("");
    lines.push(...list.map(issueLine));
  });

  return lines.join("\n");
}

function replaceBetweenMarkers(content, replacement) {
  const start = "<!-- ISSUE_INDEX_START -->";
  const end = "<!-- ISSUE_INDEX_END -->";

  if (!content.includes(start) || !content.includes(end)) {
    const withSpacing = content.endsWith("\n") ? content : `${content}\n`;
    return `${withSpacing}\n${start}\n${replacement}\n${end}\n`;
  }

  const pattern = new RegExp(
    `${start}[\\s\\S]*?${end}`,
    "m"
  );
  return content.replace(pattern, `${start}\n${replacement}\n${end}`);
}

async function run() {
  const issues = await fetchIssues();
  const generated = buildIndex(issues);

  const current = fs.existsSync(readmePath)
    ? fs.readFileSync(readmePath, "utf8")
    : "";
  const next = replaceBetweenMarkers(current, generated);

  if (current !== next) {
    fs.writeFileSync(readmePath, next, "utf8");
    console.log(`Updated ${readmePath}`);
  } else {
    console.log("No README changes needed.");
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
