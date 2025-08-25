#!/usr/bin/env bash
set -euo pipefail

# Generate a tickable checklist of current (non-outdated) unresolved threads
#
# Usage:
#   ./make_current_checklist.sh <PR_NUMBER>
#
# Env / config:
#   - GITHUB_TOKEN_PUBLIC_REPO must be set
#   - OWNER/REPO can be overridden via env. Defaults match your repo.
#
# Examples:
#   ./make_current_checklist.sh 2
#   OWNER=alphaloopbot REPO=alphaloop-core ./make_current_checklist.sh 2

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
  echo "  $0 2"
  echo "  OWNER=alphaloopbot REPO=alphaloop-core $0 2"
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
OUT_CHECKLIST="$OUTPUT_DIR/pr_${PR}_current_checklist.md"

echo "Generating current-only checklist for PR #$PR..."

# Initialize output file
{
  echo "## Current (non-outdated) unresolved threads for $OWNER/$REPO#${PR}"
  echo
  echo "- Generated: \`$(date)\`"
  echo "- Status: Current (non-outdated) threads only"
  echo
} > "$OUT_CHECKLIST"

# Paginate through all review threads
AFTER="null"
TOTAL_CURRENT=0

while :; do
  RESP=$(curl -s --max-time 10 -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN_PUBLIC_REPO" \
    https://api.github.com/graphql \
    -d '{"query":"query($o:String!,$r:String!,$n:Int!,$after:String){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100,after:$after){nodes{isResolved isOutdated path line comments(last:1){nodes{url}}} pageInfo{hasNextPage endCursor}}}}}","variables":{"o":"'"$OWNER"'","r":"'"$REPO"'","n":'"$PR"',"after":'"$AFTER"'}}')

  # Check for errors
  if jq -e '.errors' >/dev/null 2>&1 <<<"$RESP"; then
    echo "GitHub GraphQL error:"
    jq -r '.errors[] | (.message // .)' <<<"$RESP"
    exit 1
  fi

  # Extract current (non-outdated) unresolved threads
  CURRENT_THREADS=$(echo "$RESP" | jq -r '
    .data.repository.pullRequest.reviewThreads.nodes
    | map(select(.isResolved==false and .isOutdated==false))
    | .[] | "- [ ] `" + (.path // "(no file)") + ":" + ((.line // "—") | tostring) + "` → " + .comments.nodes[0].url
  ')

  # Count and append to output
  if [[ -n "$CURRENT_THREADS" ]]; then
    echo "$CURRENT_THREADS" >> "$OUT_CHECKLIST"
    COUNT=$(echo "$CURRENT_THREADS" | wc -l)
    TOTAL_CURRENT=$((TOTAL_CURRENT + COUNT))
  fi

  # Check for next page
  HAS_NEXT=$(echo "$RESP" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')
  AFTER=$(echo "$RESP" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor | @json')
  [[ "$HAS_NEXT" = "true" ]] || break
done

# Add summary
{
  echo
  echo "---"
  echo
  echo "**Total current unresolved threads: $TOTAL_CURRENT**"
  echo
  echo "💡 **Workflow:**"
  echo "1. Open this checklist in Cursor/PR description"
  echo "2. Work through items in batches by theme"
  echo "3. After each fix, click 'Resolve conversation' on the links"
  echo "4. Check off items as you complete them"
} >> "$OUT_CHECKLIST"

echo "✅ Generated checklist: $OUT_CHECKLIST"
echo "📋 Total current unresolved threads: $TOTAL_CURRENT"
