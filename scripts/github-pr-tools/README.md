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
   - `repo` (for private repositories)
   - `public_repo` (for public repositories only)
5. Copy the generated token and paste it in your `.env` file

### 3. Use the Tools

```bash
# Export comments from PR #123
make github-pr-export PR_NUMBER=123

# Analyze the exported comments
make github-pr-analyze PR_NUMBER=123

# Export and analyze in one command
make github-pr-latest PR_NUMBER=123
```

## 📁 File Structure

```
scripts/github-pr-tools/
├── export_github_pr_comments.sh    # Export PR comments to JSON
├── analyze_pr_comments.py          # Analyze exported comments
├── env.example                     # Example configuration
├── README.md                       # This file
└── output/                         # Generated files (gitignored)
    ├── .gitignore                  # Prevents committing generated files
    └── .gitkeep                    # Ensures directory is tracked
```

## 🛠️ Available Commands

### Export Comments
```bash
make github-pr-export PR_NUMBER=123
```
- Exports all comments from PR #123
- Saves to `output/pr_123_comments.json`
- Creates output directory if needed

### Analyze Comments
```bash
make github-pr-analyze PR_NUMBER=123
```
- Analyzes the exported comments
- Shows metrics and insights
- Generates structured analysis

### Export and Analyze
```bash
make github-pr-latest PR_NUMBER=123
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

### "GITHUB_TOKEN not set" Error
```bash
# Make sure you've created the .env file
cp scripts/github-pr-tools/env.example scripts/github-pr-tools/.env
# Edit the file and add your token
```

### "Permission denied" Error
- Check that your GitHub token has the correct scope
- For private repos, use `repo` scope
- For public repos, use `public_repo` scope

### "PR not found" Error
- Verify the PR number exists
- Check that your token has access to the repository

## 📝 Example Usage with CodeRabbit

```bash
# After CodeRabbit reviews your PR #456
make github-pr-latest PR_NUMBER=456

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
