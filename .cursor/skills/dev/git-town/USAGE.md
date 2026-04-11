# Git Town Skill - Usage Guide

This skill helps you execute Git Town workflow commands for efficient branch management in the current repository.

## How to Use

### Automatic Invocation

The skill is automatically invoked when you mention any of these terms in your chat:

- **Branch Creation:**
  - `git town hack`
  - `hack`
  - `create branch`
  - `new branch`
  - `start feature`
  - `feature branch`

- **Branch Syncing:**
  - `git town sync`
  - `sync`
  - `update branch`
  - `pull from main`
  - `merge main`
  - `sync branch`

- **Branch Shipping:**
  - `git town ship`
  - `ship`
  - `merge to main`
  - `complete branch`
  - `finish feature`
  - `ship branch`

- **General Git Town:**
  - `git town`
  - `branch management`
  - `git workflow`

### Manual Invocation

You can also manually invoke the skill by typing:

```
/git-town
```

Then describe what you want to do (e.g., "create a branch called add-user-auth" or "sync my current branch").

## Examples

### Creating a Feature Branch

```
I want to hack a new branch called add-user-authentication
```

or

```
git town hack add-user-authentication
```

The agent will:
1. Execute `git town hack add-user-authentication`
2. Create the branch from `main`
3. Switch to the new branch
4. Confirm the branch was created

### Syncing Your Branch

```
sync my current branch
```

or

```
git town sync
```

The agent will:
1. Execute `git town sync`
2. Pull latest changes from `main`
3. Merge them into your current branch
4. Push the updated branch to origin
5. Confirm the sync completed

**Note**: This must be run from within a feature branch (not from `main`).

### Shipping Your Branch

```
ship this branch to main
```

or

```
git town ship
```

The agent will:
1. Execute `git town ship`
2. Perform a squash merge (preserving all commit messages)
3. Merge the branch into `main`
4. Delete the branch locally
5. Delete the branch on GitHub
6. Push `main` to origin
7. Confirm the branch was shipped

**Note**: This must be run from within the feature branch you want to ship.

## Workflow Commands

### 1. `git town hack <BRANCH_NAME>`

**Purpose**: Create a new feature branch from `main`.

**When to use**:
- Starting work on a new feature
- Beginning a bug fix
- Starting work on a task or improvement

**Example**:
```
git town hack fix-login-bug
```

**What happens**:
- Creates a new branch from `main`
- Switches to the new branch
- Sets up tracking relationships

### 2. `git town sync`

**Purpose**: Update your current branch with the latest changes from `main`.

**When to use**:
- Before shipping your branch (recommended)
- When you want to incorporate latest changes from `main`
- Periodically during development to stay up-to-date

**Example**:
```
git town sync
```

**What happens**:
- Pulls latest changes from `main`
- Merges them into your current branch
- Pushes the updated branch to origin
- Handles conflicts if they arise

**Requirements**: Must be run from within a feature branch (not from `main`).

### 3. `git town ship`

**Purpose**: Complete your work and merge the feature branch to `main`.

**When to use**:
- When your feature is complete and tested
- When you're ready to merge to `main`
- After syncing your branch (recommended)

**Example**:
```
git town ship
```

**What happens**:
- Performs a squash merge (keeps all commit messages by default)
- Merges the branch into `main`
- Deletes the branch locally
- Deletes the branch on GitHub (remote)
- Pushes `main` to origin

**Requirements**: Must be run from within the feature branch you want to ship.

## Typical Workflow

The standard development workflow follows this pattern:

1. **Start work**: `git town hack <BRANCH_NAME>`
   ```
   git town hack add-dark-mode
   ```

2. **Make changes**: Edit files, commit changes as usual
   ```
   git add .
   git commit -m "feat: add dark mode toggle"
   ```

3. **Stay updated** (as needed): `git town sync`
   ```
   git town sync
   ```

4. **Complete work**: `git town ship`
   ```
   git town ship
   ```

## Configuration

The repository's Git Town configuration is stored in `git-town.toml` (main branch, ship strategy, perennial branches, forge, etc.). If the project uses Git Town, that file will already exist; otherwise the user can add one. This skill does not assume any specific branch names or strategies beyond what Git Town documents.

## What the Skill Does

✅ Executes Git Town commands directly  
✅ Creates feature branches from `main`  
✅ Syncs branches with latest `main` changes  
✅ Ships branches to `main` with squash merge  
✅ Handles branch cleanup (local and remote deletion)  
✅ Pushes changes to origin automatically  
✅ Provides clear feedback on command execution  

## What the Skill Does NOT Do

❌ Make code changes  
❌ Commit your changes (you still commit manually)  
❌ Resolve merge conflicts automatically  
❌ Review your code  
❌ Run tests before shipping  

The skill only executes Git Town commands. You're still responsible for:
- Making and committing your code changes
- Resolving merge conflicts if they occur
- Testing your code before shipping
- Reviewing your changes

## Tips

1. **Always sync before shipping**: Run `git town sync` before `git town ship` to ensure your branch is up-to-date with `main`

2. **Use descriptive branch names**: Choose clear, descriptive branch names that indicate what you're working on
   - ✅ Good: `add-user-authentication`, `fix-login-bug`, `improve-error-handling`
   - ❌ Avoid: `test`, `fix`, `update`, `changes`

3. **Commit frequently**: Make regular commits as you work - they'll all be preserved in the squash merge

4. **Test before shipping**: Make sure your code works and tests pass before running `git town ship`

5. **Handle conflicts promptly**: If `git town sync` encounters conflicts, resolve them before continuing

6. **Check your branch**: Make sure you're on the correct branch before running commands (especially `ship`)

7. **Don't ship from main**: Never run `git town ship` from `main` or perennial branches - only from feature branches

## Error Handling

If a command fails, the agent will:

1. Show you the error message
2. Explain what went wrong
3. Suggest how to resolve it

Common issues and solutions:

- **Uncommitted changes**: Git Town will stash them automatically (if configured)
- **Merge conflicts**: Resolve conflicts manually, then retry the command
- **Branch already exists**: Use a different branch name
- **Not on a feature branch**: Switch to your feature branch first
- **Remote branch doesn't exist**: This is normal for new branches - Git Town will create it

## Viewing the Skill

To view this skill in Cursor:

1. Open **Cursor Settings** (Cmd+Shift+J on Mac, Ctrl+Shift+J on Windows/Linux)
2. Navigate to **Rules**
3. Look for **git-town** in the **Agent Decides** section

## Additional Resources

- **Git Town Documentation**: https://www.git-town.com/
- **Configuration File**: `git-town.toml` in the repository root
- **Git Town Configuration Docs**: https://www.git-town.com/configuration-file
