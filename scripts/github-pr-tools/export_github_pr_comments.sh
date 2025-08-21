#!/usr/bin/env bash
set -euo pipefail

# Check if PR number is provided
if [ -z "${1:-}" ]; then
    echo "Usage: $0 <PR_NUMBER>"
    echo "Example: $0 123"
    exit 1
fi

PR_NUMBER=$1
OUTPUT_DIR="$(dirname "$0")/output"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/pr_${PR_NUMBER}_comments.json"

# Load GitHub token from .env
if [ -f "$(dirname "$0")/.env" ]; then
    source "$(dirname "$0")/.env"
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "Error: GITHUB_TOKEN not set. Put it in scripts/github-pr-tools/.env or export it."
    exit 1
fi

echo "Exporting PR #$PR_NUMBER comments to $OUTPUT_FILE..."

curl -sSf \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "https://api.github.com/repos/your-username/alphaloop-core/pulls/$PR_NUMBER/comments?per_page=100" \
    > "$OUTPUT_FILE"

echo "✅ Comments exported to $OUTPUT_FILE"
echo "💡 You can now feed this JSON to an LLM for analysis"
