# Git Town Workflow

Git Town provides a streamlined workflow for managing feature branches. Configuration is read from `git-town.toml` in the repository root when present (main branch, ship strategy, forge, etc.).

## Configuration

When the repository has a `git-town.toml` file, use it for the main branch name, ship strategy, and other options. This skill does not assume specific branch names or strategies—follow the project's Git Town configuration.

## Workflow Commands

### 1. Create Feature Branch (Hack)

**When to use**: Starting work on a new feature, bug fix, or task.

**Command**:
```bash
git town hack <BRANCH_NAME>
```

**What it does**:
- Creates a new feature branch from `main`
- Switches to the new branch
- Sets up tracking relationships

**Example**:
```bash
git town hack add-user-authentication
```

**Usage**: Use this when the user wants to:
- Start working on a new feature
- Create a branch for a bug fix
- Begin work on a task or improvement
- Mentions "create branch", "new branch", "hack", or "start feature"

### 2. Sync Branch with Main (Sync)

**When to use**: Updating the current branch with the latest changes from `main`.

**Command**:
```bash
git town sync
```

**What it does**:
- Pulls latest changes from `main`
- Merges them into the current branch
- Pushes the updated branch to origin
- Handles conflicts if they arise

**Usage**: Use this when the user wants to:
- Update their branch with latest main changes
- Sync their feature branch
- Mentions "sync", "update branch", "pull from main", or "merge main"

**Note**: This command must be run from within a feature branch (not from `main`).

### 3. Ship Branch to Main (Ship)

**When to use**: Completing work and merging the feature branch to `main`.

**Command**:
```bash
git town ship
```

**What it does**:
- Collects all commit messages from the feature branch (commits not in main)
- Creates a temporary file in `/tmp` with all commit messages
- Performs a squash merge using the collected commit messages
- Merges the branch into `main`
- Deletes the branch locally
- Deletes the branch on GitHub (remote)
- Pushes `main` to origin
- Cleans up the temporary commit message file

**Implementation Details**:

When executing `git town ship`, the agent must:

1. **Get the main branch name** (from Git Town config, or default to `main`):
   ```bash
   MAIN_BRANCH=$(git config --get git-town.main-branch 2>/dev/null || echo "main")
   ```

2. **Get the current branch name**:
   ```bash
   CURRENT_BRANCH=$(git branch --show-current)
   ```

3. **Collect commit messages** from commits in the feature branch that aren't in the main branch:
   ```bash
   git log ${MAIN_BRANCH}..${CURRENT_BRANCH} --format="%B" > /tmp/git-town-ship-msg-$$.txt
   ```
   This collects all commit messages (including multi-line messages) from commits that exist in the feature branch but not in the main branch.

4. **Execute ship with the message file**:
   ```bash
   git town ship -f /tmp/git-town-ship-msg-$$.txt
   ```

5. **Clean up** the temporary file after the command completes (success or failure):
   ```bash
   rm -f /tmp/git-town-ship-msg-$$.txt
   ```

**Complete Script Pattern**:
```bash
MAIN_BRANCH=$(git config --get git-town.main-branch 2>/dev/null || echo "main")
CURRENT_BRANCH=$(git branch --show-current)
TEMP_MSG_FILE="/tmp/git-town-ship-msg-$$.txt"
git log "${MAIN_BRANCH}..${CURRENT_BRANCH}" --format="%B" > "${TEMP_MSG_FILE}"
git town ship -f "${TEMP_MSG_FILE}"
SHIP_EXIT_CODE=$?
rm -f "${TEMP_MSG_FILE}"
exit $SHIP_EXIT_CODE
```

**Usage**: Use this when the user wants to:
- Complete and merge their feature branch
- Ship their changes to main
- Finish a feature and clean up the branch
- Mentions "ship", "merge to main", "complete branch", or "finish feature"

**Note**:
- This command must be run from within the feature branch to be shipped
- The branch will be automatically deleted locally and remotely after shipping
- All commit messages are preserved in the squash merge
- The commit message file is automatically created from all commits in the feature branch

## Workflow Sequence

The typical development workflow:

1. **Start work**: `git town hack <BRANCH_NAME>`
2. **Make changes**: Edit files, commit changes
3. **Stay updated** (as needed): `git town sync`
4. **Complete work**: `git town ship`

## Important Notes

- **Always run `git town sync` before `git town ship`** to ensure the branch is up-to-date with main
- **Ship only from feature branches** - never run `git town ship` from `main` or perennial branches
- **Branch cleanup is automatic** - branches are deleted locally and remotely after shipping
- **Commit messages are preserved** - the squash merge keeps all commit messages by default
- **Configuration is in `git-town.toml`** - the repository's Git Town settings are already configured

## Error Handling

If a command fails:
- Read the error message carefully
- Common issues:
  - Uncommitted changes: Git Town will stash them automatically (if configured)
  - Merge conflicts: Resolve conflicts manually, then continue
  - Branch already exists: Use a different branch name
- After resolving issues, retry the command

## When to Use This Skill

The agent should automatically apply this skill when the user:
- Mentions "git town", "hack", "sync", or "ship"
- Wants to create a new branch
- Wants to update their branch with main
- Wants to merge their branch to main
- Asks about branch management or Git workflow
- Mentions "feature branch", "create branch", "merge branch", or "ship branch"

The agent should execute the appropriate `git town` command directly using the terminal, not just suggest it.
