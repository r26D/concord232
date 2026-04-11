# XP Work Manager Skill - Usage Guide

This skill helps you record improvements, todos, bugs, user goals, deferred ideas, and technical debt into tracking files, and manage your iteration workflow **in the current project**. It uses a `work/` directory at the root of whatever workspace you have open, so you can use the skill in any repo and it stays scoped to that project.

## How to Use

### Automatic Invocation

The skill is automatically invoked when you use any of these trigger commands in your chat:

#### Recording New Items

- **Improvements (formerly feedback):**
  - `improve: [your request]`
  - `improve : [your request]`
  - `feedback: [your request]` (still writes to `work/IMPROVEMENTS.md`)

- **Deferred (AI or other suggestions to revisit later):**
  - `deferred: [description]`
  - `defer: [description]`

- **Technical debt:**
  - `tech debt: [description]`
  - `debt: [description]`
  - `technical debt: [description]`

- **Tasks/Features:**
  - `feat: [description]`
  - `todo: [description]`
  - `task: [description]`

- **Bug Reports:**
  - `bug: [description]`
  - `bug report: [description]`

- **User Goals/Scenarios:**
  - `goal: [description]`
  - `scenario: [description]`
  - `user_goal: [description]`
  - `user_scenario: [description]`

#### Managing Iteration Work

- **Moving Items to Iteration:**
  - `add to iteration: [reference to section]`
  - `iteration: [reference to section]`
  - `add to iteration: [new text block]` (for new items)

- **Marking Items as Done:**
  - `done: [reference to section in ITERATION.md]`

- **Moving Items to Acceptance:**
  - `needs acceptance: [reference to section in ITERATION.md]`
  - `acceptance: [reference to section in ITERATION.md]`

### Manual Invocation

You can also manually invoke the skill by typing:

```
/xp_work
```

Then describe what you want to record or manage.

## Tracking Files

The skill manages these files in a `work/` directory at the **root of your current workspace**. On first use, the agent should create any missing files with a short explanation at the top so the full set can be committed together.

| File | Purpose |
|------|---------|
| **work/IMPROVEMENTS.md** | Improvement ideas and feedback (`improve:`, `feedback:`). Legacy `work/FEEDBACK.md` is migrated automatically to this name. |
| **work/TODO.md** | Planned tasks and features (`feat:`, `todo:`, `task:`). |
| **work/BUGS.md** | Defects (`bug:`, `bug report:`). |
| **work/USER_GOALS.md** | User outcomes and scenarios (`goal:`, `scenario:`, …). |
| **work/DEFERRED.md** | Suggestions parked for later, often AI ideas (`deferred:`). |
| **work/TECH_DEBT.md** | Codebase cleanup and shortcuts (`tech debt:`, `debt:`). |
| **work/ITERATION.md** | Active iteration backlog. |
| **work/ACCEPTANCE.md** | Awaiting product owner sign-off. |

## Examples

### Recording an improvement

```
improve: The GraphQL API could have better error messages for authentication failures
```

The agent ensures `work/` files exist, appends to `work/IMPROVEMENTS.md`, and confirms.

### Recording deferred work

```
deferred: Split the upload pipeline into a separate OTP application
```

The agent appends to `work/DEFERRED.md` with source noted when clear (e.g. AI suggestion).

### Recording technical debt

```
debt: Legacy string keys in config; should migrate to structured schema
```

The agent appends to `work/TECH_DEBT.md`.

### Moving an item to iteration

```
add to iteration: Support Project-Level Tasks with Multiple Steps
```

The agent finds the section in `IMPROVEMENTS.md`, `TODO.md`, `USER_GOALS.md`, `BUGS.md`, `DEFERRED.md`, or `TECH_DEBT.md`, removes it, and appends to `work/ITERATION.md` with the correct **Source** field.

## Format Templates

Templates live in the skill’s `assets/` directory:

- `assets/improvements-template.md` — `IMPROVEMENTS.md`
- `assets/deferred-template.md` — `DEFERRED.md`
- `assets/tech-debt-template.md` — `TECH_DEBT.md`
- `assets/todo-template.md` — `TODO.md`
- `assets/bug-template.md` — `BUGS.md`
- `assets/user-goal-template.md` — `USER_GOALS.md`
- `assets/iteration-template.md` — `ITERATION.md`
- `assets/acceptance-template.md` — `ACCEPTANCE.md`

## What the Skill Does

✅ Migrates `FEEDBACK.md` to `IMPROVEMENTS.md` when needed  
✅ Ensures all canonical `work/` files exist with short purpose headers  
✅ Reads existing files to maintain format consistency  
✅ Appends entries and moves sections between files per workflow  

## What the Skill Does NOT Do

❌ Implement application code  
❌ Modify existing entries except when moving them  
❌ Decide priority or implementation for you  

## Viewing the Skill

In Cursor: **Settings → Rules** and look for **xp_work** under **Agent Decides**, or open `SKILL.md` in the installed skill folder.
