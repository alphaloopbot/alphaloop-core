#!/usr/bin/env bash
set -euo pipefail

# Export unresolved review threads from GitHub PR
# Optionally resolve all outdated+unresolved threads, then RE-FETCH to refresh the list.
#
# Usage:
#   ./export_unresolved_threads.sh <PR_NUMBER> [--resolve-outdated] [--dry-run=false]
#
# Exit codes:
#   0 -> no unresolved threads remain after (optional) cleanup
#   1 -> unresolved threads remain

# Get the actual script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load token from .env (local or project root) if present
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

# --- CLI args ---
if [ $# -lt 1 ]; then
  echo "Usage: $0 <PR_NUMBER> [--resolve-outdated] [--dry-run=false]"
  echo ""
  echo "Options:"
  echo "  --resolve-outdated    Resolve outdated+unresolved threads"
  echo "  --dry-run=true|false  Test mode (default: true)"
  echo ""
  echo "Exit codes:"
  echo "  0  No unresolved threads remain"
  echo "  1  Unresolved threads still present"
  exit 1
fi

# Help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  echo "Usage: $0 <PR_NUMBER> [--resolve-outdated] [--dry-run=false]"
  echo ""
  echo "Options:"
  echo "  --resolve-outdated    Resolve outdated+unresolved threads"
  echo "  --dry-run=true|false  Test mode (default: true)"
  echo ""
  echo "Exit codes:"
  echo "  0  No unresolved threads remain"
  echo "  1  Unresolved threads still present"
  exit 0
fi

PR="$1"; shift || true

RESOLVE_OUTDATED="false"
DRY_RUN="true"
while (( "$#" )); do
  case "$1" in
    --resolve-outdated) RESOLVE_OUTDATED="true"; shift ;;
    --dry-run=*) DRY_RUN="${1#*=}"; shift ;;
    --dry-run) DRY_RUN="true"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# --- Dependencies ---
command -v curl >/dev/null || { echo "Error: curl is required"; exit 1; }
command -v jq   >/dev/null || { echo "Error: jq is required";   exit 1; }

# --- Token ---
if [[ -z "${GITHUB_TOKEN_PUBLIC_REPO:-}" ]]; then
  echo "Error: GITHUB_TOKEN_PUBLIC_REPO not set. Put it in scripts/github-pr-tools/.env or export it."
  echo "💡 Make sure your .env file contains: GITHUB_TOKEN_PUBLIC_REPO=your_token_here"
  exit 1
fi

# Check token permissions if resolve mode is enabled
if [[ "$RESOLVE_OUTDATED" == "true" ]]; then
  echo "🔍 Checking token permissions for resolve functionality..."
  perm_check="$(curl -s --max-time 5 -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN_PUBLIC_REPO" \
    https://api.github.com/user)"

  if jq -e '.message' >/dev/null 2>&1 <<<"$perm_check"; then
    echo "❌ Token validation failed:"
    jq -r '.message' <<<"$perm_check"
    exit 1
  fi

  # Check if token has repo scope (basic check)
  scopes="$(curl -s --max-time 5 -I -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN_PUBLIC_REPO" \
    https://api.github.com/user | grep -i 'x-oauth-scopes:' || echo '')"

  if [[ "$scopes" != *"repo"* ]]; then
    echo "⚠️  Warning: Token may not have 'repo' scope required for resolving threads"
    echo "💡 If you encounter permission errors, update your token at: https://github.com/settings/tokens"
    echo "📋 Required scopes: repo, public_repo, write:discussion"
  fi
fi

# --- Output file ---
OUTPUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUTPUT_DIR"
OUTFILE="$OUTPUT_DIR/pr_${PR}_unresolved_threads.txt"

graphql() {
  local body="$1"
  curl -s --max-time 10 -H "Accept: application/vnd.github+json" \
       -H "Authorization: Bearer $GITHUB_TOKEN_PUBLIC_REPO" \
       https://api.github.com/graphql \
       -d "$body"
}

fetch_unresolved_to_file() {
  local outfile="$1"
  local after="null"
  : > "$outfile"
  {
    echo "# Unresolved review threads for $OWNER/$REPO PR #$PR"
    echo "# Generated on $(date)"
    echo "# resolve-outdated=$RESOLVE_OUTDATED dry-run=$DRY_RUN"
    echo
  } >> "$outfile"

  local unresolved_total=0
  while :; do
    local req='{"query":"query($o:String!,$r:String!,$n:Int!,$after:String){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100,after:$after){nodes{id isResolved isOutdated path line comments(last:1){nodes{url author{login}}}} pageInfo{hasNextPage endCursor}}}}}","variables":{"o":"'"$OWNER"'","r":"'"$REPO"'","n":'"$PR"',"after":'"$after"'}}'
    local resp
    resp="$(graphql "$req")"

    if jq -e '.errors' >/dev/null 2>&1 <<<"$resp"; then
      echo "Error: GitHub API returned an error:"
      jq -r '.errors[].message' <<<"$resp"
      exit 1
    fi
    if jq -e '.data.repository.pullRequest == null' >/dev/null 2>&1 <<<"$resp"; then
      echo "Error: PR #$PR not found in $OWNER/$REPO"
      exit 1
    fi

    jq -r '.data.repository.pullRequest.reviewThreads.nodes[]
      | select(.isResolved==false)
      | "\(.path):\(.line // "—") | outdated=\(.isOutdated) | author=\(.comments.nodes[0].author.login // "unknown") -> \(.comments.nodes[0].url)"' \
      <<<"$resp" >> "$outfile"

    local page_count
    page_count=$(jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false)] | length' <<<"$resp")
    unresolved_total=$((unresolved_total + page_count))

    local has_next
    has_next="$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$resp")"
    after="$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor | @json' <<<"$resp")"
    [[ "$has_next" == "true" ]] || break
  done

  echo "$unresolved_total"
}

resolve_outdated_unresolved() {
  local after="null"
  local to_resolve=()

  while :; do
    local req='{"query":"query($o:String!,$r:String!,$n:Int!,$after:String){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100,after:$after){nodes{id isResolved isOutdated} pageInfo{hasNextPage endCursor}}}}}","variables":{"o":"'"$OWNER"'","r":"'"$REPO"'","n":'"$PR"',"after":'"$after"'}}'
    local resp
    resp="$(graphql "$req")"

    if jq -e '.errors' >/dev/null 2>&1 <<<"$resp"; then
      echo "Error during resolve pass:"
      jq -r '.errors[].message' <<<"$resp"
      exit 1
    fi

    # Read IDs into array (more portable than mapfile)
    while IFS= read -r id; do
      [[ -n "$id" ]] && to_resolve+=("$id")
    done < <(jq -r '.data.repository.pullRequest.reviewThreads.nodes[]
      | select(.isResolved==false and .isOutdated==true) | .id' <<<"$resp")

    local has_next
    has_next="$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$resp")"
    after="$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor | @json' <<<"$resp")"
    [[ "$has_next" == "true" ]] || break
  done

  local count="${#to_resolve[@]}"
  if (( count == 0 )); then
    echo "No outdated+unresolved threads to resolve."
    return 0
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "Dry-run: would resolve $count outdated thread(s)."
    return 0
  fi

  echo "Resolving $count outdated thread(s)..."
  local ok=0 fail=0
  for tid in "${to_resolve[@]}"; do
    local mut='{"query":"mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}","variables":{"id":"'"$tid"'"}}'
    local r
    r="$(graphql "$mut")"
    if [[ "$(jq -r '.data.resolveReviewThread.thread.isResolved // false' <<<"$r")" == "true" ]]; then
      ok=$((ok+1))
    else
      fail=$((fail+1))
      echo "Failed to resolve $tid"
      if jq -e '.errors' >/dev/null 2>&1 <<<"$r"; then
        local error_msg
        error_msg=$(jq -r '.errors[0].message' <<<"$r")
        if [[ "$error_msg" == *"not accessible by personal access token"* ]]; then
          echo "  ⚠️  Permission error: Token needs 'repo' scope with write permissions"
          echo "  💡 Update your GitHub token at: https://github.com/settings/tokens"
          echo "  📋 Required scopes: repo, public_repo, write:discussion"
        else
          echo "  ❌ Error: $error_msg"
        fi
      fi
    fi
  done
  echo "Resolve summary: ok=$ok fail=$fail"
  if (( fail > 0 )); then
    echo "⚠️  Some threads could not be resolved due to permission issues"
    echo "💡 Consider updating your GitHub token with proper scopes"
  fi
  return 0
}

echo "==> First pass: export unresolved..."
UNRESOLVED_BEFORE=$(fetch_unresolved_to_file "$OUTFILE")
echo "Found $UNRESOLVED_BEFORE unresolved thread(s)."
echo "✅ Export written: $OUTFILE"

if [[ "$RESOLVE_OUTDATED" == "true" ]]; then
  echo "==> Resolve pass: outdated+unresolved ..."
  resolve_outdated_unresolved
  echo "==> Second pass: REFRESH export after resolving ..."
  UNRESOLVED_AFTER=$(fetch_unresolved_to_file "$OUTFILE")
  echo "Remaining unresolved after cleanup: $UNRESOLVED_AFTER"
else
  UNRESOLVED_AFTER="$UNRESOLVED_BEFORE"
fi

# Final exit status for smooth workflows / CI gating
if [[ "$UNRESOLVED_AFTER" -eq 0 ]]; then
  echo "🎉 No unresolved threads remain."
  exit 0
else
  echo "⚠️  $UNRESOLVED_AFTER unresolved threads still present. See $OUTFILE."
  exit 1
fi
