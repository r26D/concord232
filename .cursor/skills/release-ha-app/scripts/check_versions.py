#!/usr/bin/env python3
"""Check that the version string is consistent across all packaging files."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

CHECKS = [
    {
        "file": "pyproject.toml",
        "pattern": r'^version\s*=\s*"([^"]+)"',
        "flags": re.MULTILINE,
    },
    {
        "file": "setup.py",
        "pattern": r'version\s*=\s*"([^"]+)"',
        "flags": 0,
    },
    {
        "file": "addon_concord232/config.yaml",
        "pattern": r'^version:\s*"([^"]+)"',
        "flags": re.MULTILINE,
    },
    {
        "file": "addon_concord232/Dockerfile",
        "pattern": r'echo\s+"concord232==([^"]+)"',
        "flags": 0,
    },
]


def main() -> int:
    versions: dict[str, str] = {}
    errors: list[str] = []

    for check in CHECKS:
        path = ROOT / check["file"]
        if not path.exists():
            errors.append(f"  MISSING  {check['file']}")
            continue
        text = path.read_text()
        m = re.search(check["pattern"], text, check["flags"])
        if not m:
            errors.append(f"  NO MATCH {check['file']}  (pattern: {check['pattern']})")
            continue
        ver = m.group(1)
        versions[check["file"]] = ver

    if errors:
        print("Problems:\n" + "\n".join(errors))

    if not versions:
        print("No versions found.")
        return 1

    unique = set(versions.values())
    for f, v in versions.items():
        status = (
            "OK" if len(unique) == 1 else ("MISMATCH" if v != max(unique) else "OK")
        )
        print(f"  {status:8s}  {v:12s}  {f}")

    if len(unique) > 1:
        print(f"\nVersion mismatch: found {unique}")
        return 1

    print(f"\nAll versions match: {unique.pop()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
