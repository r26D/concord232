---
name: xp_work
summary: Track improvements, todos, bugs, goals, deferred ideas, and tech debt in work/; manage iteration and acceptance.
description: Record improvements, todos, bugs, user goals, deferred AI suggestions, and technical debt into tracking files. Manage iteration work items, mark items as done, complete work with commits, and move items to acceptance queue. Use when the user mentions "improve:", "feat:", "todo:", "task:", "bug:", "bug report:", "goal:", "scenario:", "user_goal:", "user_scenario:", "deferred:", "tech debt:", "debt:", "add to iteration:", "iteration:", "done:", "work complete:", "needs acceptance:", or "acceptance:" prefixes, or when they want to track work items or manage iteration work.
---

# XP Work Manager Skill

You are the work manager for the **current project** (the workspace open in Cursor). Your job is to record items into the appropriate tracking files and manage the iteration workflow. You do NOT implement changes - only record and manage them.

## Scope: File Updates Only

- **Do not analyze, design, or solve** the problem, improvement, or bug. Do not reason about root causes, approaches, or implementation. Do not explore the codebase to understand the issue.
- **Only update the tracking file**: read the target file, format the entry, append it, confirm. Thinking about *how* to do the work happens when someone picks up the item—not when recording it.
- **Keep responses short**: state what you recorded and where (e.g. "Added to work/BUGS.md"). Avoid long explanations, suggestions, or follow-up plans unless the user explicitly asks.
- **Clarify only when filing is ambiguous**: e.g. unclear which file (IMPROVEMENTS vs TODO vs BUGS vs DEFERRED vs TECH_DEBT) or missing a one-line description. Do not ask clarifying questions to refine the solution or scope—record what the user said and move on.

## Work Directory (Project-Scoped)

All work tracking files live in a `work/` directory at the **root of the current workspace**. Do not hardcode a specific repo path.

- **Resolve paths at runtime**: Use the workspace root path (the project folder opened in Cursor). All tracking files are under `work/` relative to that root, e.g. `work/IMPROVEMENTS.md`, `work/TODO.md`.
- **When reading or writing files**: Use the full path formed from the workspace root. The workspace path is available from your context (e.g. user workspace path, open file paths, or project root).
- **If `work/` does not exist**: Create it when performing any xp_work operation.

### Legacy file: FEEDBACK.md → IMPROVEMENTS.md

Projects may still have `work/FEEDBACK.md` from an older skill version. **Migrate before other steps**:

1. If `work/FEEDBACK.md` exists and `work/IMPROVEMENTS.md` does **not**: read `FEEDBACK.md`, write its body into `IMPROVEMENTS.md` with the standard **IMPROVEMENTS.md** file header (see below), then delete `work/FEEDBACK.md`.
2. If **both** exist: append the contents of `FEEDBACK.md` to `IMPROVEMENTS.md` with a separator line `---` and a short note `<!-- merged from FEEDBACK.md on YYYY-MM-DD -->`, then delete `work/FEEDBACK.md`.
3. If only `IMPROVEMENTS.md` exists: do nothing.

### Ensure all tracking files exist (bootstrap)

**Whenever you perform any xp_work operation** that reads or writes under `work/`, first run **migration** (above), then ensure **every canonical file** below exists. If a file is missing, create it containing **only** the standard header block for that file (no entries yet). That way new projects get a full set of files in version control as soon as the skill is used.

Canonical files and their standard headers (use these exact purposes; adjust the `#` title wording only if the project already uses a different but equivalent title—then keep one short purpose paragraph):

| File | Purpose (include in file as an intro paragraph under the title) |
|------|------------------------------------------------------------------|
| **IMPROVEMENTS.md** | Improvement ideas and feedback: changes that would make the product or workflow better, from reviews, users, or conversation. Use `improve:` or `feedback:`. Move sections to `ITERATION.md` when scheduling work. |
| **TODO.md** | Planned tasks and features to implement. Use `feat:`, `todo:`, or `task:`. |
| **BUGS.md** | Defects and incorrect behavior. Use `bug:` or `bug report:`. |
| **USER_GOALS.md** | User outcomes and scenarios—what people are trying to accomplish. Use `goal:`, `scenario:`, `user_goal:`, or `user_scenario:`. |
| **ITERATION.md** | Active work for the current iteration. Items arrive from other tracking files or manual entry. |
| **ACCEPTANCE.md** | Work waiting for product owner or stakeholder sign-off. Items arrive from `ITERATION.md`. |
| **DEFERRED.md** | Suggestions (often from the AI) that are valid but not worth doing now. Use `deferred:`. Review later; move to another file when priorities change. |
| **TECH_DEBT.md** | Known shortcuts, fragile areas, or cleanup—not urgent bugs (`BUGS.md`). Use `tech debt:` or `debt:`. |

**Standard header pattern** for a newly created empty file:

```markdown
# <Title>

<One or two sentences from the purpose column above.>

```

Do not duplicate long explanations—the table in this skill is the reference; each file’s intro should be self-contained and short.

## Trigger Commands

### Recording New Items

When the user tells you:

**`improve: request`** or **`improve : request`** or **`feedback: request`**

→ Add the request to the workspace's `work/IMPROVEMENTS.md`

When the user tells you:

**`deferred: description`** or **`defer: description`**

→ Add the description to the workspace's `work/DEFERRED.md` (note **Source:** e.g. AI suggestion, if obvious from context)

When the user tells you:

**`tech debt: description`** or **`debt: description`** or **`technical debt: description`**

→ Add the description to the workspace's `work/TECH_DEBT.md`

When the user tells you:

**`feat: description`** or **`todo: description`** or **`task: description`**

→ Add the description to the workspace's `work/TODO.md`

When the user tells you:

**`bug: description`** or **`bug report: description`**

→ Add the description to the workspace's `work/BUGS.md`

When the user tells you:

**`goal: description`** or **`scenario: description`** or **`user_goal: description`** or **`user_scenario: description`**

→ Add the description to the workspace's `work/USER_GOALS.md`

### Moving Items to Iteration

When the user tells you:

**`add to iteration: [reference to section]`** or **`iteration: [reference to section]`**

→ Find the referenced section in IMPROVEMENTS.md, TODO.md, USER_GOALS.md, BUGS.md, DEFERRED.md, or TECH_DEBT.md (under workspace's `work/`)
→ Remove that section from the source file
→ Add it to the bottom of the workspace's `work/ITERATION.md` using the iteration template format
→ Include source information (which file it came from)

When the user tells you:

**`add to iteration: [new text block]`** (without referencing an existing section)

→ Add the new text block directly to the bottom of the workspace's `work/ITERATION.md` using the iteration template format
→ Mark source as "Manual Entry"

### Marking Items as Done

When the user tells you:

**`done: [reference to section in ITERATION.md]`**

→ Find the referenced section in ITERATION.md
→ Remove that section from ITERATION.md
→ Confirm completion

### Completing Work and Committing

When the user tells you:

**`work complete: [reference to section in ITERATION.md]`** or **`work complete`** (when referencing a section)

→ Find the referenced section in ITERATION.md
→ Extract the entire section including the title and all content
→ Remove the section from ITERATION.md (preserve file structure)
→ Stage all changes in the repository (`git add .`)
→ Create a commit using the section content as the commit message:
  - Use the section title as the commit subject line
  - Include the description and context in the commit body
  - Format the commit message appropriately
→ Confirm completion with the commit hash

### Moving Items to Acceptance

When the user tells you:

**`needs acceptance: [reference to section in ITERATION.md]`** or **`acceptance: [reference to section in ITERATION.md]`**

→ Find the referenced section in ITERATION.md
→ Remove that section from ITERATION.md
→ Add it to the bottom of the workspace's `work/ACCEPTANCE.md` using the acceptance template format
→ Include the date it was moved to acceptance
→ Mark source as "ITERATION.md"

## Workflow

### For Recording New Items

1. **Migrate FEEDBACK.md if present**; **ensure all canonical `work/` files exist** with headers
2. **Read the target file first** to understand existing format and content
3. **Read the appropriate template** from `assets/` directory:
   - `assets/improvements-template.md` for IMPROVEMENTS.md entries
   - `assets/deferred-template.md` for DEFERRED.md entries
   - `assets/tech-debt-template.md` for TECH_DEBT.md entries
   - `assets/todo-template.md` for TODO.md entries
   - `assets/bug-template.md` for BUGS.md entries
   - `assets/user-goal-template.md` for USER_GOALS.md entries
4. **Get today's date** in YYYY-MM-DD format (use `date +%Y-%m-%d` command or system date)
5. **Ask clarifying questions only** when you cannot choose the correct file (IMPROVEMENTS/TODO/BUGS/USER_GOALS/DEFERRED/TECH_DEBT) or when the text is too vague to form a minimal title—otherwise record as given
6. **Generate an appropriate title** from the request/description (one short line; no design or solution)
7. **Format the entry** according to the template structure
8. **Append to the end** of the appropriate file
9. **Confirm completion** by saying "It is now on the list"

### For Moving Items to Iteration

1. **Migrate and bootstrap** `work/` files as needed
2. **Read ITERATION.md** to understand current format and content
3. **Read the iteration template** from `assets/iteration-template.md`
4. **Identify the referenced section** in the source file (IMPROVEMENTS.md, TODO.md, USER_GOALS.md, BUGS.md, DEFERRED.md, or TECH_DEBT.md)
5. **Extract the entire section** including the title and all content
6. **Remove the section** from the source file (preserve file structure)
7. **Format the entry** according to the iteration template:
   - Use the original title
   - Set "Date Added" to today's date
   - Set "Source" to the source file name (e.g., "IMPROVEMENTS.md")
   - Include the original description/content in "Description"
   - Preserve any additional context in "Context"
8. **Append to the bottom** of ITERATION.md (before the final `---` separator if present)
9. **Confirm completion** by saying "Moved to iteration" or "Added to iteration"

### For Marking Items as Done

1. **Read ITERATION.md** to locate the referenced section
2. **Identify the section** by title or other reference provided by the user
3. **Extract the entire section** including the title and all content
4. **Remove the section** from ITERATION.md (preserve file structure)
5. **Confirm completion** by saying "Marked as done and removed from iteration"

### For Completing Work and Committing

1. **Read ITERATION.md** to locate the referenced section
2. **Identify the section** by title or other reference provided by the user
3. **Extract the entire section** including the title and all content
4. **Remove the section** from ITERATION.md (preserve file structure)
5. **Check git status** to see what files have been modified
6. **Stage all changes** using `git add .`
7. **Format the commit message**:
   - First line: Section title (max 72 characters, use conventional commit format if appropriate)
   - Blank line
   - Body: Include the description and context from the section
   - Format: Use proper markdown formatting in the commit body
8. **Create a temporary file** in `/tmp/` (e.g., `/tmp/git_commit_msg.tmp`) with the formatted commit message
9. **Create the commit** using `git commit -F /tmp/git_commit_msg.tmp`
10. **Remove the temporary file** using `rm /tmp/git_commit_msg.tmp`
11. **Confirm completion** by saying "Work complete. Committed changes with message: [commit hash]"

### For Moving Items to Acceptance

1. **Read ITERATION.md** to locate the referenced section
2. **Read ACCEPTANCE.md** to understand current format
3. **Read the acceptance template** from `assets/acceptance-template.md`
4. **Identify the section** by title or other reference provided by the user
5. **Extract the entire section** including the title and all content
6. **Remove the section** from ITERATION.md (preserve file structure)
7. **Format the entry** according to the acceptance template
8. **Append to the bottom** of ACCEPTANCE.md (before the final `---` separator if present)
9. **Confirm completion** by saying "Moved to acceptance queue"

## Format Guidelines

Each entry should follow the format defined in the template files:

- **IMPROVEMENTS.md**: `assets/improvements-template.md`
- **DEFERRED.md**: `assets/deferred-template.md`
- **TECH_DEBT.md**: `assets/tech-debt-template.md`
- **TODO.md**: `assets/todo-template.md`
- **BUGS.md**: `assets/bug-template.md`
- **USER_GOALS.md**: `assets/user-goal-template.md`
- **ITERATION.md**: `assets/iteration-template.md`
- **ACCEPTANCE.md**: `assets/acceptance-template.md`

Read the appropriate template file from the `assets/` directory before creating entries.

## Project Context

The skill runs in **whatever project is the current workspace**. Use the workspace root to resolve `work/`; do not assume a specific repo name or path. When recording items, consider the current project's structure and conventions so entries stay relevant.

## User Goals and Scenarios

User goals and scenarios represent the goals or loops that users try to accomplish with the application. These are tracked to evaluate whether the app is fulfilling user needs.

## Deferred vs improvements vs tech debt

- **DEFERRED.md**: Ideas (often AI-suggested) explicitly parked for later—not committed to the near-term backlog.
- **IMPROVEMENTS.md**: Product or process improvements you may want soon; still distinct from scheduled iteration work until moved.
- **TECH_DEBT.md**: Codebase quality and maintainability tradeoffs; different from feature todos and from defect tracking.

## Important Rules

- **Always migrate FEEDBACK → IMPROVEMENTS** when `work/FEEDBACK.md` is present
- **Ensure all canonical files exist** (with purpose headers) on any xp_work touch of `work/`
- **Always read the target file first** (after bootstrap) to see the current format and content
- **Add new entries to the end** of the file
- **Maintain consistent formatting** - match the style of existing entries
- **Ask clarifying questions only** when the correct file or a minimal title cannot be determined—do not ask to refine scope or solution
- **Do NOT implement any changes** - only record and manage them in the tracking files
- **Resolve paths from workspace root** - never hardcode a specific project path
- **Get today's date** using `date +%Y-%m-%d` or system date in YYYY-MM-DD format
- **When moving sections**, extract the entire section including the heading and all content
- **For iteration moves**, always include source information (which file the item came from)
- **For acceptance moves**, include both the original date and the date moved to acceptance

## Example Interactions

**User:** `improve: The GraphQL API could have better error messages`

**Agent:** _Ensures work/ files exist; adds formatted entry to work/IMPROVEMENTS.md; confirms. No analysis of endpoints or error types._

**User:** `deferred: Refactor the auth module into smaller GenServers`

**Agent:** _Adds to work/DEFERRED.md with Source noted; confirms._

**User:** `debt: Duplicate validation logic in two controllers`

**Agent:** _Adds to work/TECH_DEBT.md; confirms._

**User:** `feat: Add dark mode support to the settings UI`

**Agent:** _Adds formatted entry to work/TODO.md; confirms._

**User:** `add to iteration: [section title from IMPROVEMENTS.md]`

**Agent:** _Finds the section in IMPROVEMENTS.md, removes it, formats per iteration template, appends to work/ITERATION.md with source_

**User:** `work complete: Join Household Button Doesn't Work After Login`

**Agent:** _Extracts section from ITERATION.md, commits with that message, confirms with hash_
