# Claude Code Skill System Research

**Project:** claude-legado (/novel skill)
**Researched:** 2026-04-06
**Knowledge cutoff:** August 2025 (training data)
**Overall confidence:** MEDIUM — based on training data; web/filesystem access blocked during research session. Verify against current Claude Code docs before building.

---

## Executive Summary

Claude Code's "skill" system is actually the **custom slash commands** feature — markdown prompt files (`.md`) stored in `~/.claude/commands/` (global) or `.claude/commands/` (project-local). When a user types `/novel` in a Claude Code session, Claude reads the corresponding `.md` file and executes the prompt described within it.

**Critical finding for this project:** Custom slash commands are prompt templates, not executable scripts. They do not directly take over the terminal. The correct architecture for `/novel` is: the `.md` command file instructs Claude to run a separate executable (Node.js/Python script) via the Bash tool, and that script handles the interactive TUI. Claude Code's Bash tool does support long-running processes with interactive output.

The PROJECT.md references `.claude/skills/` as the directory — this name appears to be project-specific convention or an alias. The canonical Claude Code directory is `.claude/commands/`. Verify which name the installed Claude Code version actually uses.

---

## 1. Where Do Skills/Commands Live?

### Directory Structure (HIGH confidence — training data + PROJECT.md corroboration)

```
~/.claude/commands/          # Global commands — available in all projects
  novel.md                   # Defines /novel globally

.claude/commands/            # Project-local commands — available only in this project
  novel.md                   # Defines /novel for this project only
```

**Note:** PROJECT.md says `.claude/skills/` — this may be:
- An alternate name Claude Code also supports (LOW confidence)
- The project spec author's convention/error (MEDIUM confidence)
- A version-specific name (LOW confidence)

**ACTION REQUIRED:** Before building, check the actual Claude Code docs or run `claude --help` to confirm whether `commands/` or `skills/` is the correct directory name. If both work, prefer `commands/` as it matches official documentation.

### Lookup Order

Project-local commands take precedence over global. If `.claude/commands/novel.md` exists, it overrides `~/.claude/commands/novel.md`.

---

## 2. Skill Entry Point Format

### Markdown Prompt Files (HIGH confidence)

A command file is a `.md` file whose content is a system prompt / instructions for Claude. When invoked, Claude reads the file and acts on it.

```markdown
# /novel — Chinese Novel Reader

Read a Chinese web novel chapter, streaming the content character by character
in the style of a Claude AI response. Run the novel reader script:

$ARGUMENTS

Execute: bash ~/.claude-legado/reader.js $ARGUMENTS
```

### Arguments (MEDIUM confidence)

Commands can receive arguments via `$ARGUMENTS` placeholder in the markdown. Whatever the user types after `/novel` gets substituted.

Example:
- User types: `/novel search 斗破苍穹`
- `$ARGUMENTS` becomes: `search 斗破苍穹`

### What the Prompt Actually Does

The markdown file is not a shell script — it's instructions to Claude. Claude then uses its available tools (Bash, Read, Write, etc.) to execute the described task. So the pattern is:

```
/novel invoked
  → Claude reads novel.md
  → Claude sees instruction "run this script"
  → Claude calls Bash tool to execute the script
  → Script output appears in the terminal
```

This is the critical architectural insight: **the skill file delegates to an external executable**.

---

## 3. Interactive TUI — Can a Skill Take Over the Terminal?

### The Core Problem (HIGH confidence on the constraint)

Claude Code runs as an interactive session where Claude reads/writes to the terminal. A custom slash command does not bypass this — it runs within Claude's tool execution context. This means:

1. Claude calls `Bash(script.js)` to run your reader
2. The Bash tool captures stdout and returns it to Claude
3. Claude displays the output in its response area

This is **NOT** a raw PTY handoff. The Bash tool is not a transparent pipe to the terminal.

### What This Means for Interactive TUI (HIGH confidence)

A traditional TUI (blessed, ink, ncurses) that:
- Uses ANSI escape sequences to position cursor
- Reads raw keystrokes via stdin
- Redraws the screen in place

...will likely **not work correctly** when run through Claude's Bash tool, because:

- The Bash tool may not give the subprocess a proper PTY (pseudo-terminal)
- Stdin may not be connected to the user's keyboard (it goes to Claude)
- ANSI sequences may be stripped or interpreted differently
- Output is typically captured and returned as a block, not streamed character-by-character to the raw terminal

### Possible Workarounds (MEDIUM confidence — requires testing)

**Option A: Pure stdout streaming, no cursor control**
- Script outputs text line by line
- No cursor repositioning or screen clearing
- Claude streams the output as its "response"
- This is the simplest approach and most likely to work
- For the camouflage use case, this may be ideal — it looks like Claude typing

**Option B: Spawn a detached terminal process**
- The command file instructs Claude to run: `tmux new-window "python reader.py"` or `xterm -e reader.py`
- Opens a new terminal window entirely outside Claude's control
- Full PTY, full keyboard, full TUI possible
- Breaks the "looks like Claude" camouflage

**Option C: Use a named pipe / separate terminal**
- Reader runs in background, outputs to a file
- Claude's skill tails that file
- Complex, unlikely to be worth it

**Option D: Test if Bash tool passes PTY**
- Some versions of Claude Code's Bash tool DO pass a PTY to child processes
- If so, a TUI script launched via `Bash(node reader.js)` might work
- This requires empirical testing — cannot be confirmed from training data alone

**Recommendation for /novel:** Start with Option A (streaming stdout, no cursor control). The character-by-character typewriter output in the terminal scroll is actually the desired camouflage effect. Use ANSI color codes only (not cursor positioning), which are more likely to pass through correctly.

---

## 4. stdin/stdout/stderr Interaction

### stdout (MEDIUM confidence)

When Claude runs a Bash command, stdout is captured and returned to Claude, which then displays it. For streaming display:
- Output appears as Claude's response text
- Line buffering behavior depends on Claude Code version
- `console.log()` / `print()` output appears in the response

### stderr (MEDIUM confidence)

stderr from Bash tool commands typically appears separately or is merged — behavior may vary by Claude Code version. For the novel reader:
- Use stderr only for fatal errors
- All display output should go to stdout

### stdin (LOW confidence — needs verification)

This is the critical unknown. When Claude calls `Bash(node reader.js)`:
- Is stdin connected to `/dev/null`?
- Is stdin the terminal (allowing keypress detection)?
- Is stdin a pipe from Claude?

If stdin is not the terminal, the reader cannot detect keypresses for navigation (next page, quit, etc.).

**Likely workaround:** Use signals instead of stdin:
- The script reads from a control file (e.g., `~/.claude-legado/control`)
- User interaction is through separate Claude commands (`/novel next`, `/novel quit`)
- Or: Script self-advances on a timer, no interactive control needed during reading

**Alternative:** Use `process.stdin.setRawMode()` and test whether it throws — if it does, fall back to timed auto-advance mode.

---

## 5. Long-Running Processes

### Can a Skill Spawn a Long-Running Process? (MEDIUM confidence)

**Within a Bash tool call:** A script can run for as long as Claude Code's tool timeout allows. Claude Code does not have a hard per-command timeout documented in training data, but very long processes (minutes) may be terminated.

**As background process:** The command could launch a background process (`node reader.js &`) and return immediately. The process continues running but its output is no longer visible in Claude's session.

**Novel reader loop design options:**

Option 1 — Blocking, chapter-at-a-time:
```
/novel read "Book Title" chapter 5
  → Claude calls Bash("node reader.js read 'Book Title' 5")
  → Script fetches chapter, streams text to stdout
  → Returns when chapter is done
  → User calls /novel read "Book Title" chapter 6 for next
```
This is simplest and most reliable. No persistent process needed.

Option 2 — Long-running session:
```
/novel start "Book Title"
  → Claude launches reader in background
  → Outputs "Novel reader started. Use /novel next, /novel prev to navigate."
  → Background process runs, writes to screen somehow
```
This is architecturally complex and likely problematic given terminal ownership issues.

**Recommendation:** Use Option 1 — chapter-per-invocation. Each `/novel` call fetches and streams one chapter. Simple, reliable, fits Claude's tool execution model naturally.

---

## 6. Examples of Interactive Skills

### Known Examples from Training Data (MEDIUM confidence)

Claude Code ships with built-in commands like `/help`, `/clear`, `/config` — but these are built-in, not examples of custom skill interactivity.

Community examples of custom slash commands (from training data):
- `/deploy` — runs a deployment script, streams output
- `/test` — runs test suite and formats results
- `/review` — reads files and returns a code review

These are all "one-shot: invoke, get output, done" patterns. No examples of persistent interactive TUI sessions via custom commands are documented in training data.

The closest to interactive is commands that run scripts with streaming output — this is the pattern that `/novel` should follow.

---

## 7. Invocation Format

### Slash Command Syntax (HIGH confidence)

```
/commandname [arguments]
```

Examples for this project:
```
/novel                        # Show library / resume last book
/novel search 斗破苍穹         # Search for a book
/novel read "Book" 5          # Read chapter 5
/novel next                   # Read next chapter (if tracking state)
/novel add source.json        # Add a book source
```

### File Naming (HIGH confidence)

Command name = filename without `.md`:
- `novel.md` → `/novel`
- `novel-search.md` → `/novel-search`

Subcommands are typically handled within a single command file by passing arguments to the script, not by creating separate files for each subcommand.

### Namespace (MEDIUM confidence)

Commands from `.claude/commands/` are available project-locally. Global commands from `~/.claude/commands/` are available everywhere. There is no documented namespacing collision resolution other than project-local taking precedence.

---

## 8. Limitations

### Hard Limitations (HIGH confidence)

1. **No direct terminal ownership** — skills cannot take over the TTY; they operate within Claude's output stream
2. **No persistent state between invocations** — each `/novel` call is a fresh Claude context unless state is stored externally (file, database)
3. **Prompt file only, no binary** — the `.md` file is instructions to Claude, not an executable
4. **Depends on Claude's tools** — if Bash tool is not permitted (settings.local.json), the script cannot be executed

### Soft Limitations (MEDIUM confidence)

5. **Timeout on long-running Bash calls** — very long chapters (30+ min streams) may hit timeouts
6. **PTY availability unknown** — interactive stdin may not work; needs testing
7. **ANSI escape support partial** — cursor positioning likely stripped; colors likely pass through
8. **Context window** — very long chapter content returned from Bash tool consumes context; use streaming/chunked output

### The `settings.local.json` Context

This project's `.claude/settings.local.json` currently only allows `git add` and `git commit` via Bash. **The `/novel` skill needs Bash permissions to run the reader script.** This will require updating settings to also allow `Bash(node:*)` or `Bash(*reader*:*)` or broadly `Bash(*)`.

---

## 9. Technology Stack Recommendation

### For the Reader Script (MEDIUM-HIGH confidence)

**Recommended: Node.js**

Rationale:
- Claude Code itself is Node.js — Node is guaranteed to be available in any Claude Code environment
- Better HTTP client libraries (axios, node-fetch, got) with streaming support
- Strong JSON parsing for legado book source format
- Process control via `process.stdout.write()` for character-by-character output
- `readline` module for potential stdin handling
- npm ecosystem for HTML parsing (cheerio), CSS selectors (legado's rule format uses CSS selectors)

**Against Python:**
- Not guaranteed to be installed in all Claude Code environments
- Would need `pip install` for dependencies
- Slightly more complex to package

**Against Shell (bash/zsh):**
- Terrible at JSON parsing (legado book source format is complex JSON)
- No good HTTP client with cookie handling
- Cannot do character-by-character streaming easily

### Node.js Libraries for the Reader

| Library | Purpose | Confidence |
|---------|---------|-----------|
| `axios` or `node-fetch` | HTTP fetching of novel content | HIGH |
| `cheerio` | HTML parsing for legado CSS selector rules | HIGH |
| `chalk` or raw ANSI | Terminal color for camouflage styling | HIGH |
| `conf` or `lowdb` | Local state storage (progress, library) | MEDIUM |
| No blessed/ink | Avoid — PTY requirements likely fail in Bash tool | HIGH |

### Output Strategy for Camouflage

```javascript
// Character-by-character streaming to stdout
async function streamText(text, delayMs = 30) {
  for (const char of text) {
    process.stdout.write(char);
    await sleep(delayMs);
  }
}
```

This works within Claude's output stream — Claude's Bash tool returns output as it's produced (stream mode), so the typewriter effect IS achievable if Claude Code's Bash tool supports streaming stdout. **Needs verification.**

---

## 10. Architecture for This Project

### Recommended Structure

```
.claude/
  commands/
    novel.md              # Slash command definition (or skills/ — verify)

~/.claude-legado/         # User data (outside project)
  reader.js               # Main executable (or src/ tree)
  library.json            # User's bookshelf
  progress.json           # Per-book reading position
  sources/                # Installed legado book source JSONs
    default.json
```

Or alternatively, keep the reader script in the project:

```
.claude/
  commands/
    novel.md

src/
  reader.js               # Main script invoked by novel.md
  lib/
    source-parser.js      # Legado book source JSON parser
    http-client.js        # Fetches novel content
    renderer.js           # Formats output as fake Claude response
    state.js              # Reads/writes progress.json
```

### novel.md Command File (Recommended Pattern)

```markdown
# Novel Reader

Read a Chinese web novel, streaming chapter content styled as a Claude response.

Run the novel reader with the provided arguments:

```bash
node /path/to/reader.js $ARGUMENTS
```

Display the output exactly as returned. Do not summarize, modify, or add commentary.
```

**Key instruction:** "Do not summarize or modify output" is critical — without this, Claude may try to helpfully summarize the novel content instead of passing it through.

---

## Open Questions / Verification Needed

| Question | Priority | How to Verify |
|----------|----------|---------------|
| Is it `commands/` or `skills/` directory? | CRITICAL | `ls ~/.claude/` or check official docs |
| Does Bash tool stream stdout in real-time? | CRITICAL | Test with `node -e "setInterval(() => process.stdout.write('.'), 100)"` |
| Is stdin connected to terminal in Bash tool? | HIGH | Test with `node -e "process.stdin.setRawMode(true)"` — throws if no PTY |
| What is the Bash tool timeout? | MEDIUM | Run a `sleep 300` and see if it's killed |
| Does settings.local.json need updating for Bash? | HIGH | Check current settings — yes, it does |
| Does Claude pass through ANSI color codes? | MEDIUM | Test with a script that outputs colored text |
| Are `$ARGUMENTS` dollar-sign substitutions supported? | HIGH | Check current Claude Code docs |

---

## Sources

- Training data (knowledge cutoff August 2025) — MEDIUM confidence
- `/home/ubwzwd/Code/claude_legado/.planning/PROJECT.md` — project spec reference to `.claude/skills/` directory
- Official Claude Code documentation: https://docs.anthropic.com/en/docs/claude-code/ (not accessible during research session — verify directly)
- Claude Code GitHub: https://github.com/anthropics/claude-code (not accessible — verify directly)

**NOTE:** Web access and filesystem access to `~/.claude/` were blocked during this research session. All findings are from training data. Before implementation, verify the "Open Questions" table above by direct testing or consulting current documentation.
