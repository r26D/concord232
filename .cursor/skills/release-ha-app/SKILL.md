---
name: release-ha-app
description: >-
  Sync version strings and update the Home Assistant add-on package for a new
  release. Use when bumping the version, releasing a new version, packaging for
  Home Assistant, or updating the add-on.
---

# Release: Home Assistant App

Workflow for cutting a new version of concord232 and keeping the HA add-on in
sync. This covers version bumps across all files and add-on changelog updates.

## Version Locations

Four files carry the version string. **All must match.**

| File | Pattern | Example |
|------|---------|---------|
| `pyproject.toml` | `version = "X.Y.Z"` under `[project]` | `version = "0.15.11"` |
| `setup.py` | `version="X.Y.Z"` in `setup()` | `version="0.15.11"` |
| `addon_concord232/config.yaml` | `version: "X.Y.Z"` | `version: "0.15.11"` |
| `addon_concord232/Dockerfile` | `echo "concord232==X.Y.Z"` (cache-bust) | `echo "concord232==0.15.11"` |

## Workflow

Copy this checklist and track progress:

```
Release Progress:
- [ ] Step 1: Determine new version
- [ ] Step 2: Validate current versions
- [ ] Step 3: Bump all version strings
- [ ] Step 4: Update addon CHANGELOG
- [ ] Step 5: Validate updated versions
- [ ] Step 6: Summary
```

### Step 1: Determine new version

Ask the user for the new version, or infer from context (e.g. "bump patch").
Apply semver: `MAJOR.MINOR.PATCH`.

- **patch**: bug fixes, small improvements
- **minor**: new features, backward-compatible
- **major**: breaking changes

### Step 2: Validate current versions

Run the validation script to confirm current state:

```bash
python .cursor/skills/release-ha-app/scripts/check_versions.py
```

If versions are already out of sync, flag this to the user before proceeding.

### Step 3: Bump all version strings

Update exactly these four locations with the new version:

1. **`pyproject.toml`** — `version = "X.Y.Z"` under `[project]`
2. **`setup.py`** — `version="X.Y.Z"` in the `setup()` call
3. **`addon_concord232/config.yaml`** — `version: "X.Y.Z"`
4. **`addon_concord232/Dockerfile`** — the `echo "concord232==X.Y.Z"` cache-bust line

Use exact string replacement for each. Do not rewrite entire files.

### Step 4: Update addon CHANGELOG

Prepend a new section to `addon_concord232/CHANGELOG.md`:

```markdown
## X.Y.Z

- <description of changes>
```

Ask the user what changed, or summarize from recent git commits:

```bash
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD
```

If the root `CHANGELOG.md` also needs updating, ask the user — don't assume.

### Step 5: Validate updated versions

Run validation again to confirm all four files now match:

```bash
python .cursor/skills/release-ha-app/scripts/check_versions.py
```

All four must report the same version. If not, fix before proceeding.

### Step 6: Summary

Report to the user:

- Old version → New version
- Files modified
- Remind them to commit, push to `main`, and (optionally) tag the release

Do **not** commit or push automatically — let the user decide when.
