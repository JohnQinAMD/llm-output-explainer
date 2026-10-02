#!/usr/bin/env bash
# Live facts about a GitHub PR, for an explainer page.
#
# Usage: pr_facts.sh <owner/repo> <pr-number> [checkout-dir] [body-out-file]
#
# Prints the PR's current state (open/merged, merge commit, head and base SHAs,
# size) and its commits. If checkout-dir has those commits, each one's diffstat
# is printed too. If body-out-file is given, the current PR body is saved there.
#
# Optional auth: set GH_TOKEN_FILE to a file holding a GitHub token. It is
# passed to curl through a process substitution, never argv or a temp file.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <owner/repo> <pr-number> [checkout-dir] [body-out-file]" >&2
  exit 2
fi
repo=$1
pr=$2
dir=${3:-}
body_out=${4:-}
api="https://api.github.com/repos/$repo"

# No temp files, because /tmp can be full. The token goes through a curl config
# read from a process substitution, so it never appears in argv.
tokcfg() {
  if [[ -n "${GH_TOKEN_FILE:-}" && -r "$GH_TOKEN_FILE" ]]; then
    printf 'header = "Authorization: Bearer %s"\n' "$(tr -d '[:space:]' < "$GH_TOKEN_FILE")"
  fi
}
get() { curl -sSfL -K <(tokcfg) -H "Accept: application/vnd.github+json" "$1"; }

pr_json=$(get "$api/pulls/$pr")
commits_json=$(get "$api/pulls/$pr/commits?per_page=100")
merge_sha=$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("merge_commit_sha") or "" if d.get("merged") else "")' <<<"$pr_json")
merge_json='{}'
if [[ -n "$merge_sha" ]]; then merge_json=$(get "$api/commits/$merge_sha"); fi

# JSON goes through pipes (/dev/fd), not argv: a big PR's merge commit carries every patch.
python3 - <(printf '%s' "$pr_json") <(printf '%s' "$commits_json") <(printf '%s' "$merge_json") "$body_out" <<'EOF'
import json, re, sys
pr = json.load(open(sys.argv[1]))
commits = json.load(open(sys.argv[2]))
merge = json.load(open(sys.argv[3]))
body_out = sys.argv[4]
state = "MERGED" if pr.get("merged") else pr["state"].upper()
if pr.get("draft"):
    state += " (draft)"
print(f"title:    {pr['title']}")
print(f"url:      {pr['html_url']}")
print(f"state:    {state}")
if pr.get("merged"):
    who = (pr.get("merged_by") or {}).get("login")
    print(f"merged:   {pr['merged_at']} by {who}, merge commit {pr['merge_commit_sha'][:10]}")
    msg = (merge.get("commit") or {}).get("message", "")
    trailers = [l for l in msg.splitlines() if re.match(r"(Co-authored-by|Signed-off-by):", l, re.I)]
    print(f"  merge commit subject:  {msg.splitlines()[0] if msg else '?'}")
    print(f"  merge commit trailers: {'; '.join(trailers) if trailers else 'none'}")
print(f"author:   {pr['user']['login']}")
head_repo = (pr["head"].get("repo") or {}).get("full_name")
print(f"head:     {pr['head']['sha']}  ({head_repo}:{pr['head']['ref']})")
print(f"base:     {pr['base']['ref']} at {pr['base']['sha'][:10]}")
print(f"size:     {pr['commits']} commits, {pr['changed_files']} files, +{pr['additions']} -{pr['deletions']}")
labels = ", ".join(l["name"] for l in pr.get("labels", []))
if labels:
    print(f"labels:   {labels}")
print(f"updated:  {pr['updated_at']}")
print("commits:")
for c in commits:
    subj = c["commit"]["message"].splitlines()[0]
    print(f"  {c['sha']}  {subj}")
if body_out:
    with open(body_out, "w") as f:
        f.write(pr.get("body") or "")
    print(f"body:     saved to {body_out}")
EOF

if [[ -n "$dir" ]]; then
  echo "diffstats (from $dir):"
  python3 -c 'import json,sys; [print(c["sha"]) for c in json.load(sys.stdin)]' <<<"$commits_json" |
  while read -r sha; do
    if git -C "$dir" cat-file -e "$sha^{commit}" 2>/dev/null; then
      stat=$(git -C "$dir" diff --shortstat "$sha~1" "$sha" | sed 's/^ *//')
      echo "  ${sha:0:10}  $stat"
    else
      echo "  ${sha:0:10}  (not in this checkout; fetch the PR head to get it)"
    fi
  done
fi
