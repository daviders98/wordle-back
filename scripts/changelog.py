#!/usr/bin/env python3
import subprocess
import json
import os
from pathlib import Path

OUTPUT = Path("./public/changelog.json")


def bump_version(version: str) -> str:
    version = version.lstrip("v")
    major, minor, patch = map(int, version.split("."))
    patch += 1

    if patch >= 10:
        patch = 0
        minor += 1
    if minor >= 10:
        minor = 0
        major += 1

    return f"v{major}.{minor}.{patch}"


def generate_changelog():
    print("📦 Generating changelog...")

    # Run git log command
    git_log = subprocess.run(
        ["git", "log", "--reverse", "--pretty=format:{\"message\":\"%s\",\"author\":\"%an\",\"date\":\"%cI\"},"] ,
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    if not git_log:
        print("⚠️ No commits found.")
        return

    json_string = f"[{git_log[:-1]}]"  # Remove trailing comma
    commits = json.loads(json_string)

    version = "v0.0.0"
    changelog = []

    for commit in commits:
        changelog.append({
            "version": version,
            "commits": [commit],
        })
        version = bump_version(version)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(changelog, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(commits)} commits exported to {OUTPUT}")


if __name__ == "__main__":
    generate_changelog()
