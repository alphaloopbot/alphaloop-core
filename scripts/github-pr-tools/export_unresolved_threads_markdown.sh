#!/usr/bin/env bash
set -euo pipefail

# Export unresolved review threads (with full comment content) to Markdown.
#
# Usage:
#   ./export_unresolved_threads_markdown.sh <PR_NUMBER>
#
# Env / config:
#   - GITHUB_TOKEN_PUBLIC_REPO must be set (classic PAT with at least `public_repo` for public repos,
#     or a fine-grained PAT with Pull requests: Read).
#   - OWNER/REPO can be overridden via env. Defaults match your repo.
#
# Examples:
#   OWNER=alphaloopbot REPO=alphaloop-core ./export_unresolved_threads_markdown.sh 2

# Get the actual script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Load token from .env files (optional) ---
if [ -f "$SCRIPT_DIR/.env" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.env"
fi
if [ -f "$SCRIPT_DIR/../../.env" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/../../.env"
fi

# --- Config ---
OWNER="${OWNER:-alphaloopbot}"
REPO="${REPO:-alphaloop-core}"

# --- Args ---
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PR_NUMBER>"
  echo ""
  echo "Examples:"
  echo "  $0 123"
  echo "  OWNER=alphaloopbot REPO=alphaloop-core $0 123"
  exit 1
fi
PR="$1"

# --- Deps ---
command -v curl >/dev/null || { echo "Error: curl is required"; exit 1; }
command -v jq   >/dev/null || { echo "Error: jq is required";   exit 1; }

# --- Token ---
if [[ -z "${GITHUB_TOKEN_PUBLIC_REPO:-}" ]]; then
  echo "Error: GITHUB_TOKEN_PUBLIC_REPO not set. Put it in a .env or export it."
  echo "💡 Make sure your .env file contains: GITHUB_TOKEN_PUBLIC_REPO=your_token_here"
  exit 1
fi

# --- Output ---
OUTPUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUTPUT_DIR"
OUT_MD="$OUTPUT_DIR/pr_${PR}_unresolved_threads.md"
TMP_JSON="$(mktemp)"

rest_api() {
  local endpoint="$1"
  curl -s --max-time 10 -H "Accept: application/vnd.github+json" \
       -H "Authorization: Bearer $GITHUB_TOKEN_PUBLIC_REPO" \
       "https://api.github.com/repos/$OWNER/$REPO$endpoint"
}

echo "Fetching review comments for PR #$PR..."

# Fetch all review comments using REST API
RESP="$(rest_api "/pulls/$PR/comments?per_page=100")"

# Check for errors
if jq -e '.message' >/dev/null 2>&1 <<<"$RESP"; then
  echo "GitHub API error:"
  jq -r '.message' <<<"$RESP"
  exit 1
fi

# Check if PR exists
if jq -e '.[0].id' >/dev/null 2>&1 <<<"$RESP"; then
  echo "Found $(jq 'length' <<<"$RESP") review comments"
else
  echo "Error: PR #$PR not found in $OWNER/$REPO or no review comments"
  exit 1
fi

# Process comments and group by thread
echo "Processing comments..."

# Create Markdown header
{
  echo "# Review Comments for \`$OWNER/$REPO\` PR #$PR"
  echo
  echo "- Generated: \`$(date)\`"
  echo "- Total comments: **$(jq 'length' <<<"$RESP")**"
  echo
  echo "---"
  echo
} > "$OUT_MD"

# Group comments by file and line, then output as Markdown
jq -r '
  # Group by file and line
  group_by(.path + ":" + (.line | tostring))
  | .[]
  | "## " + (.[0].path // "(no file)") + ":" + (.[0].line | tostring) + "\n"
  + (
    .[]
    | "- **" + (.user.login // "unknown") + "** · _" + .created_at + "_  \n"
    + "  [link](" + .html_url + ")  \n"
    + "  " + (.body | gsub("\r"; "") | gsub("\n"; "\n  "))
    + "\n\n"
  )
  + "---\n"
' <<<"$RESP" >> "$OUT_MD"

echo "✅ Wrote $OUT_MD"

# Clean up temp
rm -f "$TMP_JSON"
