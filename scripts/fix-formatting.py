#!/usr/bin/env python3
"""
Automatic formatting fixer for common code style issues.

This script runs before commits to automatically fix common formatting issues
like line length, import sorting, and other style problems.
"""

from pathlib import Path
import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main() -> int:
    """Main function to run all formatting fixes."""
    print("🚀 Running automatic formatting fixes...")

    # Get the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    success = True

    # 1. Run ruff to fix import sorting, line length, and other issues
    success &= run_command(
        ["poetry", "run", "ruff", "check", ".", "--fix"],
        "Fixing code style issues with ruff",
    )

    # 2. Run ruff format to ensure consistent formatting
    success &= run_command(
        ["poetry", "run", "ruff", "format", "."], "Formatting code with ruff-format"
    )

    # 3. Run ruff check again to see remaining issues (but don't fail)
    print("🔍 Checking remaining style issues...")
    try:
        result = subprocess.run(
            ["poetry", "run", "ruff", "check", "."], capture_output=True, text=True
        )
        if result.stdout.strip():
            print("⚠️  Some issues remain (these may need manual attention):")
            print(result.stdout)
        else:
            print("✅ All style issues resolved!")
    except subprocess.CalledProcessError as e:
        print("⚠️  Some issues remain (these may need manual attention):")
        if e.stdout:
            print(e.stdout)
        success = False

    if success:
        print("🎉 All formatting fixes completed successfully!")
        return 0
    else:
        print("❌ Some formatting fixes failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    import os

    sys.exit(main())
