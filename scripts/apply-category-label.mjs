// Reads the "분류" field of an issue created from the 메모 form
// and adds a label with the same name.
import fs from "node:fs";
import process from "node:process";

const token = process.env.GITHUB_TOKEN;
const repo = process.env.GITHUB_REPOSITORY;
const eventPath = process.env.GITHUB_EVENT_PATH;

if (!token || !repo || !eventPath) {
  throw new Error("GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_EVENT_PATH are required.");
}

const { issue } = JSON.parse(fs.readFileSync(eventPath, "utf8"));
if (!issue) {
  console.log("Not an issue event.");
  process.exit(0);
}

// Issue forms render each field as "### <label>\n\n<value>".
const match = String(issue.body || "").match(/^###\s*분류\s*\r?\n+\s*([^\r\n]+)/m);
const category = match ? match[1].trim() : "";

if (!category || category === "_No response_") {
  console.log("No category field found.");
  process.exit(0);
}

if ((issue.labels || []).some((l) => l.name === category)) {
  console.log(`Label "${category}" already set.`);
  process.exit(0);
}

const res = await fetch(
  `https://api.github.com/repos/${repo}/issues/${issue.number}/labels`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "issue-category-labeler",
    },
    body: JSON.stringify({ labels: [category] }),
  }
);

if (!res.ok) {
  throw new Error(`GitHub API error (${res.status}): ${await res.text()}`);
}
console.log(`Added label "${category}" to #${issue.number}.`);
