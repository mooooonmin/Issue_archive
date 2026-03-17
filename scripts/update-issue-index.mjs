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

function issueLine(issue) {
  const title = String(issue.title || "").replace(/\r?\n/g, " ").trim();
  const labels = Array.isArray(issue.labels)
    ? issue.labels
        .map((l) => (typeof l === "string" ? l : l?.name))
        .filter(Boolean)
        .map((name) => `\`${name}\``)
        .join(", ")
    : "";

  const state = issue.state === "open" ? "open" : "closed";
  const suffix = labels ? ` - ${state} - ${labels}` : ` - ${state}`;
  return `- [#${issue.number}](${issue.html_url}) ${title}${suffix}`;
}

function buildIndex(issues) {
  const openIssues = issues.filter((i) => i.state === "open");
  const closedIssues = issues.filter((i) => i.state === "closed");

  const lines = [];
  lines.push("## Issue Index");
  lines.push("");
  lines.push(
    `업데이트: ${toKstIso()} (KST) / 총 ${issues.length}개 (Open ${openIssues.length}, Closed ${closedIssues.length})`
  );
  lines.push("");

  lines.push("### Open");
  if (openIssues.length === 0) {
    lines.push("- 없음");
  } else {
    lines.push(...openIssues.map(issueLine));
  }
  lines.push("");

  lines.push("### Closed");
  if (closedIssues.length === 0) {
    lines.push("- 없음");
  } else {
    lines.push(...closedIssues.map(issueLine));
  }

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
