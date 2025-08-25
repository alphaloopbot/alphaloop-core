# GitHub PR Tools

Tools for exporting and analyzing GitHub Pull Request comments, perfect for working with CodeRabbit and other review tools.

## 🚀 Quick Start

### 1. Setup GitHub Token

```bash
# Copy the example configuration
cp scripts/github-pr-tools/env.example scripts/github-pr-tools/.env

# Edit the .env file and add your GitHub token
# Replace YOUR_GITHUB_TOKEN_HERE with your actual token
```

### 2. Get a GitHub Token

1. Go to [GitHub.com → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "AlphaLoop PR Tools"
4. Select scopes:
   - `repo` (for private repositories and resolving threads)
   - `public_repo` (for public repositories only)
   - `write:discussion` (for resolving review threads)
   - `read:org` (for organization repositories)
5. Copy the generated token and paste it in your `.env` file

**Note**: For resolving outdated threads, the token needs `repo` scope with write permissions.

### 3. Use the Tools

```bash
# Export comments from PR #123
make github-pr-export PR=123

# Analyze the exported comments
make github-pr-analyze PR=123

# Export and analyze in one command
make github-pr-latest PR=123
```

## 📁 File Structure

```
scripts/github-pr-tools/
├── export_github_pr_comments.sh    # Export PR comments to JSON
├── export_unresolved_threads.sh    # Export unresolved review threads
├── export_unresolved_threads_markdown.sh  # Export threads with full content to Markdown
├── make_current_checklist.sh       # Generate tickable checklist of current threads
├── analyze_pr_comments.py          # Analyze exported comments
├── env.example                     # Example configuration
├── README.md                       # This file
└── output/                         # Generated files (gitignored)
    ├── .gitignore                  # Prevents committing generated files
    └── .gitkeep                    # Ensures directory is tracked
```

## 🛠️ Available Commands

### Basic Usage
```bash
# Export unresolved threads (read-only)
./scripts/github-pr-tools/export_unresolved_threads.sh 123

# Export and resolve outdated threads
./scripts/github-pr-tools/export_unresolved_threads.sh 123 --resolve-outdated --dry-run=false

# Dry-run mode (test without making changes)
./scripts/github-pr-tools/export_unresolved_threads.sh 123 --resolve-outdated --dry-run=true

# Export with full comment content to Markdown
./scripts/github-pr-tools/export_unresolved_threads_markdown.sh 123

# Generate current-only checklist
./scripts/github-pr-tools/make_current_checklist.sh 123
```

### Export Comments
```bash
make github-pr-export PR=123
```
- Exports all comments from PR #123
- Saves to `output/pr_123_comments.json`
- Creates output directory if needed

### Export Unresolved Threads
```bash
make github-pr-unresolved PR=123
```
- Exports unresolved review threads from PR #123
- Saves to `output/pr_123_unresolved_threads.txt`
- Shows file paths, line numbers, author, and comment URLs

### Export and Resolve Outdated Threads
```bash
make export-pr-unresolved-resolve PR=123
```
- Exports unresolved threads AND resolves outdated ones
- Automatically cleans up outdated+unresolved threads
- Refreshes the export after resolution
- Perfect for CI/CD workflows

### Export Unresolved Threads to Markdown
```bash
make export-pr-unresolved-markdown PR=123
```
- Exports all review comments with full content to Markdown
- Creates detailed Markdown report with all comment bodies
- Shows file paths, line numbers, authors, and timestamps
- Uses REST API (works with `public_repo` scope)
- Perfect for detailed review analysis

### Generate Current-Only Checklist
```bash
make export-pr-current-checklist PR=123
```
- Generates tickable checklist of current (non-outdated) unresolved threads
- Creates focused list for PR review workflow
- Includes direct links to each thread for easy navigation
- Uses GraphQL API (requires proper token scopes)
- Perfect for systematic review and resolution tracking

### Analyze Comments
```bash
make github-pr-analyze PR=123
```
- Analyzes the exported comments
- Shows metrics and insights
- Generates structured analysis

### Export and Analyze
```bash
make github-pr-latest PR=123
```
- Combines both operations
- Perfect for quick analysis

## 📊 Output Analysis

The analysis tool provides:

- **Comment Statistics**: Total comments, unique commenters
- **File Analysis**: Most commented files, file types affected
- **Suggestion Types**: Code suggestions, questions, approvals
- **Severity Assessment**: Critical, important, minor issues
- **Actionable Insights**: Patterns and recommendations

## 🔒 Security

- **Token Protection**: Never commit your `.env` file (it's gitignored)
- **Output Isolation**: Generated files are in separate directory
- **Scope Limitation**: Use minimal required GitHub permissions

## 🐛 Troubleshooting

### "GITHUB_TOKEN_PUBLIC_REPO not set" Error
```bash
# Make sure you've created the .env file
cp scripts/github-pr-tools/env.example scripts/github-pr-tools/.env
# Edit the file and add your token as GITHUB_TOKEN_PUBLIC_REPO=your_token_here
```

### "Permission denied" Error
- Check that your GitHub token has the correct scope
- For private repos, use `repo` scope
- For public repos, use `public_repo` scope

### "PR not found" Error
- Verify the PR number exists
- Check that your token has access to the repository

### "Resource not accessible by personal access token" Error
- Your token needs additional permissions for resolving threads
- Update your token with these scopes:
  - `repo` (Full control of private repositories)
  - `public_repo` (Access public repositories)
  - `write:discussion` (Write access to discussions)
- Go to [GitHub Token Settings](https://github.com/settings/tokens) to update

## 📝 Example Usage with CodeRabbit

```bash
# After CodeRabbit reviews your PR #456
make github-pr-latest PR=456

# This will:
# 1. Export all CodeRabbit comments
# 2. Analyze the feedback patterns
# 3. Show actionable insights for improvement
```

## 🤝 Contributing

To add new analysis features:

1. Modify `analyze_pr_comments.py`
2. Add new metrics or insights
3. Update this README
4. Test with real PR data

## 📚 Related Documentation

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Personal Access Tokens Guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [CodeRabbit Integration](https://coderabbit.ai/)
