#!/usr/bin/env python3
"""
Analyze GitHub PR comments and generate structured LLM prompts.
"""

import json
import sys
from typing import Any


def load_pr_comments(file_path: str) -> list[dict[str, Any]]:
    """Load PR comments from JSON file."""
    with open(file_path) as f:
        return json.load(f)


def analyze_comments(comments: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze comments and extract metrics."""
    analysis: dict[str, Any] = {
        "total_comments": len(comments),
        "commenters": set(),
        "files_affected": set(),
        "suggestion_types": {
            "refactor": 0,
            "bug": 0,
            "security": 0,
            "performance": 0,
            "documentation": 0,
            "other": 0,
        },
        "severity": {"high": 0, "medium": 0, "low": 0},
    }

    for comment in comments:
        # Extract commenter
        if "user" in comment and "login" in comment["user"]:
            analysis["commenters"].add(comment["user"]["login"])

        # Extract file affected
        if "path" in comment:
            analysis["files_affected"].add(comment["path"])

        # Analyze comment content
        body = comment.get("body", "").lower()

        # Categorize by type
        if "refactor" in body or "suggestion" in body:
            analysis["suggestion_types"]["refactor"] += 1
        elif "bug" in body or "fix" in body:
            analysis["suggestion_types"]["bug"] += 1
        elif "security" in body:
            analysis["suggestion_types"]["security"] += 1
        elif "performance" in body:
            analysis["suggestion_types"]["performance"] += 1
        elif "documentation" in body or "readme" in body:
            analysis["suggestion_types"]["documentation"] += 1
        else:
            analysis["suggestion_types"]["other"] += 1

        # Categorize by severity
        if "critical" in body or "high priority" in body:
            analysis["severity"]["high"] += 1
        elif "medium" in body or "important" in body:
            analysis["severity"]["medium"] += 1
        else:
            analysis["severity"]["low"] += 1

    # Convert sets to lists for JSON serialization
    analysis["commenters"] = list(analysis["commenters"])
    analysis["files_affected"] = list(analysis["files_affected"])

    return analysis


def generate_llm_prompt(comments: list[dict[str, Any]], analysis: dict[str, Any]) -> str:
    """Generate a structured prompt for LLMs."""
    prompt = f"""# PR Code Review Analysis

## Summary
- **Total Comments**: {analysis["total_comments"]}
- **Commenters**: {", ".join(analysis["commenters"])}
- **Files Affected**: {len(analysis["files_affected"])}

## Comment Types
- Refactor Suggestions: {analysis["suggestion_types"]["refactor"]}
- Bug Fixes: {analysis["suggestion_types"]["bug"]}
- Security Issues: {analysis["suggestion_types"]["security"]}
- Performance: {analysis["suggestion_types"]["performance"]}
- Documentation: {analysis["suggestion_types"]["documentation"]}
- Other: {analysis["suggestion_types"]["other"]}

## Severity Distribution
- High Priority: {analysis["severity"]["high"]}
- Medium Priority: {analysis["severity"]["medium"]}
- Low Priority: {analysis["severity"]["low"]}

## Detailed Comments

"""

    for i, comment in enumerate(comments, 1):
        prompt += f"""### Comment {i}
**File**: {comment.get("path", "Unknown")}
**Line**: {comment.get("line", "Unknown")}
**Author**: {comment.get("user", {}).get("login", "Unknown")}
**Type**: {comment.get("in_reply_to_id", "line")}

{comment.get("body", "No content")}

---
"""

    prompt += """
## Your Task
Please analyze these PR comments and provide:

1. **Priority Assessment**: Which comments should be addressed first?
2. **Action Items**: Specific tasks to implement the suggestions
3. **Code Examples**: Show how to implement the suggested changes
4. **Risk Assessment**: Any potential issues with the suggestions
5. **Summary**: Overall quality and completeness of the review

Focus on actionable, specific recommendations.
"""

    return prompt


def main() -> None:
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_pr_comments.py <comments_json_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    comments = load_pr_comments(file_path)
    analysis = analyze_comments(comments)

    # Generate output
    output_file = file_path.replace(".json", "_llm_prompt.txt")
    prompt = generate_llm_prompt(comments, analysis)

    with open(output_file, "w") as f:
        f.write(prompt)

    print("✅ Analysis complete!")
    print(
        f"📊 Summary: {analysis['total_comments']} comments from {len(analysis['commenters'])} reviewers"
    )
    print(f"📝 LLM prompt saved to: {output_file}")


if __name__ == "__main__":
    main()
