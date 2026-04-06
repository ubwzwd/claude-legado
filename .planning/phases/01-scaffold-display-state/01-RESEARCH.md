# Phase 1: Scaffold, Display, State - Research

**Researched:** 2026-04-07
**Domain:** Python CLI skill scaffold, Rich streaming display, JSON state persistence, Claude Code slash command format
**Confidence:** HIGH

## Summary

Phase 1 wires the `/novel` Claude Code skill with a Python `src/novel/` package, implements a character-by-character streaming display engine using Rich, and persists reading state to `~/.claude-legado/`. All content is hardcoded fake data. No HTTP, no rule engine, no real book sources.

The core technical challenge is the streaming display engine: it must look indistinguishable from a real Claude AI response at a glance. This means variable delays, occasional burst chunks, CJK double-width handling, and a fake reasoning preamble. Rich handles CJK width natively via its internal `_cell_widths` table — no manual wcwidth math needed. Character-by-character output uses `sys.stdout.write()` + `flush()` for raw text streaming, with Rich reserved for structured elements (headers, navigation hints).

The Claude Code skill file lives at `.claude/commands/novel.md` (or `.claude/skills/novel/SKILL.md` — both formats work). It instructs Claude to run `cd /path/to/repo && python -m novel $ARGUMENTS` in a Bash block. This is the standard pattern for skills that delegate entirely to an external script.

**Primary recommendation:** Build the package structure first (01-01), implement the streaming engine second (01-02), add state persistence third (01-03). All three plans depend on the `src/novel/` package existing; 01-02 and 01-03 can be parallelized after 01-01 completes since they touch different modules.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Project Structure**
- D-01: `src/novel/` Python package (src-layout). Entry point at `src/novel/__main__.py` or equivalent so `python -m novel` works.
- D-02: Skill file lives at `.claude/commands/novel.md`. Invokes via `cd /path/to/repo && python -m novel $ARGUMENTS` in a Bash block.
- D-03: No separate `novel.py` at root — keep the package structure clean from day one so Phase 2+ rule engine modules land naturally inside `src/novel/`.

**Camouflage Framing**
- D-04: Prepend a short italicized fake reasoning block before chapter text begins. Mimics Claude's extended thinking mode.
- D-05: After the fake reasoning block, stream chapter content character-by-character using DISP-02/DISP-03 timing (15–40ms per char, longer pauses at `。！？`, occasional 8–15 char bursts).
- D-06: No fake prompt echo or Q&A framing — the reasoning block + streaming text is sufficient camouflage.

**Fake Hardcoded Content**
- D-07: Ship 3 fake chapters of actual Chinese web novel prose (public-domain or generated content that reads like xianxia/wuxia). Enough for next/prev navigation and state persistence to be meaningfully testable.
- D-08: Fake book metadata: title, author, and chapter list are all hardcoded. The "current book" is auto-loaded so `/novel` works with no prior shelf setup.
- D-09: Chapter content is long enough to look like a real chapter at a glance (>=500 Chinese characters per chapter).

**Streaming Display Engine**
- D-10: Use `rich.console.Console` in live/streaming mode (no alternate screen, scrollback preserved — DISP-05).
- D-11: CJK double-width: rely on Rich's built-in wcwidth handling. No manual width math — Rich handles this correctly when the console width is queried from the terminal.
- D-12: Chapter header (number + title) printed before content starts (DISP-06). Navigation hint block printed after content ends (DISP-07).

**State Persistence**
- D-13: State file at `~/.claude-legado/state.json`. Bookshelf at `~/.claude-legado/shelf.json`. Sources directory at `~/.claude-legado/sources/`.
- D-14: `/novel` with no args resumes from last saved position. If state is empty, auto-loads the hardcoded fake book and starts at chapter 1.
- D-15: State written after each chapter display (not interactively mid-chapter — chapter-per-invocation design).

**Stubbed Subcommands**
- D-16: `search`, `toc`, `shelf`, `use` each print a one-line stub message rather than erroring out. All eight subcommands must be registered.

### Claude's Discretion
- Exact wording of the fake reasoning block
- Whether to use `time.sleep` or `asyncio` for streaming delays (prefer sync for Phase 1 simplicity)
- Packaging details (`pyproject.toml` vs `setup.py`, exact package layout within `src/novel/`)
- Whether to add a `requirements.txt` or go straight to `pyproject.toml`

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SKILL-01 | Claude Code skill file at `.claude/commands/novel.md` triggers `/novel` command | Verified: `.claude/commands/` format confirmed via official docs; `$ARGUMENTS` substitution supported |
| SKILL-02 | `/novel` with no args streams current chapter (or prompts to pick if shelf empty) | Entry point dispatch: `__main__.py` checks `sys.argv`; fallback to hardcoded fake book (D-14) |
| SKILL-03 | `/novel next` advances to next chapter and streams content | `sys.argv[1] == 'next'` dispatch; increments chapter index in state.json |
| SKILL-04 | `/novel prev` goes back one chapter and streams content | `sys.argv[1] == 'prev'` dispatch; decrements chapter index in state.json |
| SKILL-05 | `/novel search <query>` searches and shows results | Stub: prints "search: not yet implemented — available in Phase 4" |
| SKILL-06 | `/novel toc` shows chapter list | Stub: prints "toc: not yet implemented — available in Phase 4" |
| SKILL-07 | `/novel shelf` shows saved books with reading progress | Stub: prints "shelf: not yet implemented — available in Phase 4" |
| SKILL-08 | `/novel use <path>` loads a book source JSON file | Stub: prints "use: not yet implemented — available in Phase 3" |
| DISP-01 | Chapter content streams character-by-character mimicking Claude AI response | `sys.stdout.write(char); sys.stdout.flush()` in tight loop with `time.sleep` |
| DISP-02 | Variable delay per character (15–40ms base, longer pauses at `。！？`) | `random.uniform(0.015, 0.040)` base; 150ms for sentence-end punctuation |
| DISP-03 | Occasional burst chunks (8–15 chars) to mimic real LLM token streaming | 15% probability burst of `random.randint(8, 15)` chars with single short delay |
| DISP-04 | CJK double-width characters handled correctly | Rich's `cell_len('你') == 2` verified; Console respects wcwidth internally |
| DISP-05 | Output uses Rich Console in streaming mode — no alternate screen buffer | `Console(markup=False, highlight=False)` with no `with console.screen()` — scrollback preserved |
| DISP-06 | Chapter header shown before content (chapter number + title) | `console.print(f"[bold]第{n}章 {title}[/bold]")` before streaming loop |
| DISP-07 | Navigation hint shown at end of each chapter | `console.print(...)` after streaming loop; always printed |
| STATE-01 | Reading state persisted to `~/.claude-legado/state.json` | `pathlib.Path.home() / '.claude-legado' / 'state.json'`; `json.dump` after each chapter |
| STATE-02 | `/novel` with no args resumes from last saved position automatically | Load state.json on startup; if missing or empty, bootstrap with fake book at chapter 0 |
| STATE-03 | Bookshelf persisted to `~/.claude-legado/shelf.json` | Written during bootstrap; updated when `use` is implemented in Phase 3 |
| STATE-04 | Loaded book sources persisted to `~/.claude-legado/sources/` | Directory created on init; not actively written in Phase 1 (source engine is Phase 3) |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| rich | 14.3.3 (latest) / 13.7.1 (installed) | Console output, CJK-aware width, formatted headers and hints | Industry standard for Python terminal UI; built-in wcwidth table handles CJK correctly [VERIFIED: pip registry] |
| pathlib | stdlib | `~/.claude-legado/` directory management | No external dep; `Path.home() / '.claude-legado'` is idiomatic [VERIFIED: Python 3.12 stdlib] |
| json | stdlib | State and shelf serialization | Sufficient for flat state objects; `ensure_ascii=False` preserves Chinese text [VERIFIED: Python 3.12 stdlib] |
| sys / time / random | stdlib | `sys.argv` dispatch, `time.sleep` for character delays, `random` for variable timing | No external deps for Phase 1 streaming [VERIFIED: Python 3.12 stdlib] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.2 (installed) | Unit tests for state logic and dispatcher | Wave 0 gap: no tests exist yet; needed for validation architecture |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `time.sleep` + `sys.stdout.write` | `asyncio` event loop | asyncio is overkill for Phase 1 — no concurrent I/O needed; sync is simpler and decided by user (Claude's Discretion) |
| `rich.Console` for headers/hints | plain `print()` | Rich gives bold/italic markup for free; use Rich for structured output, raw stdout for character streaming |
| `pyproject.toml` + setuptools | `requirements.txt` only | pyproject.toml is the modern standard; setuptools 68.1.2 is available and supports src-layout [VERIFIED: pip show setuptools] |

**Installation:**
```bash
pip install rich
# rich 14.3.3 is latest; 13.7.1 already installed on this machine
```

**Version verification:** [VERIFIED: pip registry 2026-04-07]
- `rich`: installed 13.7.1, latest 14.3.3 — both work for Phase 1; 13.7.1 has all needed CJK features
- `pytest`: installed 9.0.2 (latest available on this machine) — adequate

## Architecture Patterns

### Recommended Project Structure
```
src/
└── novel/
    ├── __init__.py          # package marker
    ├── __main__.py          # entry point: python -m novel
    ├── commands.py          # subcommand dispatcher (next/prev/search/toc/shelf/use)
    ├── display.py           # streaming engine + Rich header/hint printing
    ├── state.py             # state.json and shelf.json read/write
    └── data/
        └── fake_book.py     # hardcoded fake chapters (3 chapters, >=500 CJK chars each)
.claude/
└── commands/
    └── novel.md             # Claude Code skill file
tests/
└── test_state.py            # STATE-01 through STATE-04 tests
└── test_commands.py         # SKILL-01 through SKILL-08 dispatch tests
pyproject.toml               # package config, installs `src/novel/`
```

### Pattern 1: Skill File with Direct Python Invocation

**What:** `.claude/commands/novel.md` instructs Claude to run a Bash command. The entire skill delegates to Python — Claude does nothing after running the command.

**When to use:** When the skill is a complete standalone program (not an AI task). The skill file is purely a launcher.

**Example:**
```markdown
---
name: novel
description: Read Chinese web novels in your Claude Code session
argument-hint: "[next|prev|search|toc|shelf|use] [args]"
disable-model-invocation: true
allowed-tools: Bash(python -m novel:*)
---

Run the following command and display the output exactly as-is:

```bash
cd /path/to/repo && python -m novel $ARGUMENTS
```

Do not interpret the output. Do not add commentary. Stream it directly.
```

[VERIFIED: official Claude Code docs — code.claude.com/docs/en/slash-commands; `.claude/commands/` format confirmed; `$ARGUMENTS` substitution works; `allowed-tools` and `disable-model-invocation` frontmatter supported]

**Critical note on path:** The skill file must use an absolute path or a path derivable at runtime. Since the skill lives inside the project repo, using `${CLAUDE_SKILL_DIR}` is NOT reliable here (that's for `skills/` subdirectories). The cleanest approach: use `python -m novel` from within the repo directory, which means the skill must `cd` to the repo root first. The repo path must be hardcoded or the skill can detect it with `!` injection.

**Alternative approach (avoids hardcoded path):**
```markdown
```!
echo "$(git -C $(dirname $0)/../../ rev-parse --show-toplevel)"
```
```
Or more simply, if the user always runs from the repo:
```bash
python -m novel $ARGUMENTS
```
(relies on the working directory already being the repo root when Claude Code is open)

### Pattern 2: `__main__.py` Argument Dispatcher

**What:** `src/novel/__main__.py` reads `sys.argv` and routes to command handlers.

**When to use:** All invocations of `python -m novel`.

**Example:**
```python
# src/novel/__main__.py
import sys
from novel.commands import dispatch

def main():
    args = sys.argv[1:]
    dispatch(args)

if __name__ == "__main__":
    main()
```

```python
# src/novel/commands.py
from novel.display import stream_chapter
from novel.state import load_state, save_state, bootstrap_state

STUB_COMMANDS = {
    'search': 'search: not yet implemented — available in Phase 4',
    'toc':    'toc: not yet implemented — available in Phase 4',
    'shelf':  'shelf: not yet implemented — available in Phase 4',
    'use':    'use: not yet implemented — available in Phase 3',
}

def dispatch(args):
    if not args or args[0] not in ('next', 'prev', 'search', 'toc', 'shelf', 'use'):
        cmd = args[0] if args else None
        if cmd in STUB_COMMANDS:
            print(STUB_COMMANDS[cmd])
            return
        # Default: stream current chapter
        _stream_current()
        return

    cmd = args[0]
    if cmd in STUB_COMMANDS:
        print(STUB_COMMANDS[cmd])
    elif cmd == 'next':
        _advance(+1)
    elif cmd == 'prev':
        _advance(-1)
```

[ASSUMED] — Pattern is standard Python CLI idiom, not verified against a specific external doc.

### Pattern 3: Character Streaming with Variable Timing

**What:** Stream content character-by-character using `sys.stdout.write` + `flush` with `time.sleep` for per-character delays.

**When to use:** DISP-01 through DISP-03.

**Example:**
```python
# src/novel/display.py
import sys
import time
import random

PAUSE_LONG = 0.15   # 。！？ — sentence-end pause
PAUSE_MED  = 0.06   # ，、；
DELAY_MIN  = 0.015  # 15ms base
DELAY_MAX  = 0.040  # 40ms base
BURST_PROB = 0.15   # 15% chance of burst chunk
BURST_MIN  = 8
BURST_MAX  = 15

def _char_delay(ch: str) -> float:
    if ch in '。！？':
        return PAUSE_LONG
    if ch in '，、；':
        return PAUSE_MED
    return random.uniform(DELAY_MIN, DELAY_MAX)

def stream_text(text: str) -> None:
    """Stream text character-by-character with LLM-like timing."""
    i = 0
    while i < len(text):
        # Decide burst or single
        if random.random() < BURST_PROB and i + BURST_MIN < len(text):
            chunk_size = random.randint(BURST_MIN, BURST_MAX)
            chunk = text[i:i + chunk_size]
            sys.stdout.write(chunk)
            sys.stdout.flush()
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            i += chunk_size
        else:
            ch = text[i]
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(_char_delay(ch))
            i += 1
    sys.stdout.write('\n')
    sys.stdout.flush()
```

[VERIFIED: time.sleep granularity at 15ms confirmed accurate on this machine (Linux/WSL2 — measured 15.2ms actual)]

### Pattern 4: Rich for Structured Output (Headers + Hints)

**What:** Use `rich.console.Console` for the fake reasoning preamble, chapter header, and navigation hints. Use raw stdout only for character streaming.

**When to use:** Non-streaming structural elements.

**Example:**
```python
from rich.console import Console

console = Console(markup=True, highlight=False)

def print_chapter_header(chapter_num: int, title: str) -> None:
    console.print(f"\n[bold cyan]第{chapter_num}章  {title}[/bold cyan]\n")

def print_reasoning_preamble() -> None:
    console.print("[italic dim]*正在准备章节内容...*[/italic dim]\n")

def print_nav_hints(chapter_index: int, total: int) -> None:
    console.print("\n")
    hints = []
    if chapter_index < total - 1:
        hints.append("[dim]/novel next[/dim] — 下一章")
    if chapter_index > 0:
        hints.append("[dim]/novel prev[/dim] — 上一章")
    hints.append("[dim]/novel toc[/dim] — 目录")
    console.print("  " + "   |   ".join(hints))
```

[VERIFIED: Rich Console markup=True syntax confirmed; Console(markup=False) tested on installed 13.7.1]

### Pattern 5: State JSON with Atomic-ish Write

**What:** Read state.json on startup, write after every chapter. Use a temp file + rename for safety (prevents corrupt state from a crash mid-write).

**When to use:** STATE-01, STATE-02.

**Example:**
```python
# src/novel/state.py
import json
import pathlib
import tempfile
import os

STATE_DIR = pathlib.Path.home() / '.claude-legado'
STATE_FILE = STATE_DIR / 'state.json'
SHELF_FILE = STATE_DIR / 'shelf.json'
SOURCES_DIR = STATE_DIR / 'sources'

DEFAULT_STATE = {
    'current_book': None,
    'chapter_index': 0,
    'source': None,
}

def ensure_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

def load_state() -> dict:
    ensure_dirs()
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_STATE)

def save_state(state: dict) -> None:
    ensure_dirs()
    tmp = STATE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(STATE_FILE)
```

[ASSUMED] — Atomic write via tmp+rename is a standard pattern; not verified against specific doc. `pathlib.Path.replace()` is stdlib.

### Anti-Patterns to Avoid

- **Alternate screen buffer (`Console().screen()`):** Would eat the scrollback — violates DISP-05. Never use `with console.screen()`.
- **`print()` for chapter streaming:** `print()` adds a newline after each char, destroying the streaming illusion. Use `sys.stdout.write(ch); sys.stdout.flush()`.
- **Rich markup in streamed content:** Chinese novel prose may contain `[` or `]` that Rich would interpret as markup tags. Set `markup=False` for the Console used in streaming, OR use raw stdout (which doesn't parse markup at all). Use a separate `Console(markup=True)` for the structured elements.
- **`asyncio` for Phase 1:** Adds complexity with no benefit — no concurrent I/O in Phase 1. `time.sleep` is correct here.
- **`state.json` write on every character:** Only write after the full chapter is displayed (D-15). Writing on every character would be thousands of file writes per chapter.
- **Hardcoding repo path in skill file:** Will break when the project is cloned to a different path. The skill must use a relative invocation or dynamic path resolution.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CJK double-width calculation | Manual Unicode block range math | `rich.cells.cell_len()` / Rich Console's built-in wcwidth table | Rich's `_cell_widths` covers all CJK Unified Ideographs, Hangul, fullwidth forms; manual ranges miss edge cases [VERIFIED: cell_len('你好') == 4 on rich 13.7.1] |
| Terminal width detection | `os.get_terminal_size()` custom wrapper | `rich.console.Console().width` | Rich already wraps get_terminal_size with fallback to 80 [VERIFIED: Console().width returns 80 on this machine] |
| Styled terminal output | ANSI escape codes by hand | `rich.console.Console` with markup | Rich handles terminal capability detection, Windows compatibility, etc. |
| State directory creation | Custom exists-check logic | `pathlib.Path.mkdir(parents=True, exist_ok=True)` | One line, handles race conditions, idiomatic [VERIFIED: stdlib] |

**Key insight:** Rich's CJK handling is the most important "don't hand-roll" item. The community has invested significant effort getting the wcwidth tables right; any manual approach will have bugs with edge-case CJK ranges.

## Common Pitfalls

### Pitfall 1: Rich Markup Eating CJK Square Brackets
**What goes wrong:** Chinese text sometimes contains `【` and `】` (fullwidth brackets), or the novel prose uses `[` and `]` for emphasis. Rich's default `markup=True` tries to parse these as style tags and produces garbled output or raises `MarkupError`.
**Why it happens:** Rich Console parses `[anything]` as markup by default.
**How to avoid:** Use `Console(markup=False, highlight=False)` OR stream via raw `sys.stdout` for all novel content. Use a separate `Console(markup=True)` only for the header/hints where you control the text.
**Warning signs:** `MarkupError` exceptions, or Chinese text disappearing from output.

### Pitfall 2: Skill File Path Resolution Breaks on Different Machines
**What goes wrong:** `.claude/commands/novel.md` with `cd /home/user/projects/claude-legado && python -m novel $ARGUMENTS` fails when cloned to a different path.
**Why it happens:** The path is hardcoded in the skill file.
**How to avoid:** Use a path-agnostic invocation. Since Claude Code always opens in the project root, `python -m novel $ARGUMENTS` without a `cd` should work if the skill is invoked from that project. Alternatively, use `!` injection to dynamically determine the project root: `cd !`git rev-parse --show-toplevel`` && python -m novel $ARGUMENTS`.
**Warning signs:** `ModuleNotFoundError: No module named 'novel'` — Python can't find the package because it's not run from the repo root.

### Pitfall 3: `python -m novel` Fails Without Package Installation
**What goes wrong:** `python -m novel` raises `ModuleNotFoundError` because `src/novel/` is not on `sys.path`.
**Why it happens:** With a src-layout, `src/` is not automatically on the Python path unless the package is installed (`pip install -e .`).
**How to avoid:** Either (a) install the package with `pip install -e .` as a setup step, OR (b) the skill file does `cd /repo && PYTHONPATH=src python -m novel $ARGUMENTS`, OR (c) use `python src/novel/__main__.py $ARGUMENTS` as a fallback. Option (a) is cleanest for future phases.
**Warning signs:** `ModuleNotFoundError: No module named 'novel'` on first run.

### Pitfall 4: State File Corruption on Keyboard Interrupt
**What goes wrong:** User presses Ctrl+C mid-stream; if state is being written at that moment, `state.json` gets truncated and future runs fail.
**Why it happens:** `json.dump()` to an open file is not atomic — partial writes are possible.
**How to avoid:** Write to a `.tmp` file, then use `Path.replace()` (atomic on POSIX). State is written only after streaming completes (D-15), so Ctrl+C during streaming leaves the previous valid state intact.
**Warning signs:** `json.JSONDecodeError` on startup; always handle in `load_state()` with fallback to DEFAULT_STATE.

### Pitfall 5: CJK Text Wrapping Mid-Character-Stream
**What goes wrong:** When streaming character-by-character, the terminal may wrap a CJK char mid-word in a way that looks wrong.
**Why it happens:** The terminal doesn't know a double-width character is coming until it's written; wrapping happens after the fact.
**How to avoid:** This is mostly handled by Rich's width awareness for structured output. For raw streaming, wrapping is inherent in terminal behavior and acceptable — the text reflows correctly. The requirement (DISP-04) is "no overflow, no misaligned lines," which means the chapter as a whole must render cleanly when scrolled back, not that every in-flight character wraps perfectly.
**Warning signs:** Lines that end with half a CJK character width (visible misalignment in scrollback).

### Pitfall 6: `$ARGUMENTS` Is Empty for Default `/novel` Invocation
**What goes wrong:** `sys.argv` in `__main__.py` only has `['__main__']` — no extra arg. Code that does `sys.argv[1]` without checking raises `IndexError`.
**Why it happens:** `/novel` with no arguments passes an empty string or nothing as `$ARGUMENTS` depending on the Claude Code version.
**How to avoid:** Always guard: `args = sys.argv[1:]` then `if not args` for the default case.
**Warning signs:** `IndexError: list index out of range` on `/novel` with no arguments.

## Code Examples

Verified patterns from testing on this machine:

### CJK Width Verification
```python
# Source: rich.cells module (rich 13.7.1, installed)
from rich.cells import cell_len
assert cell_len('你') == 2      # single CJK char = 2 cells
assert cell_len('你好') == 4    # two CJK chars = 4 cells
assert cell_len('hello你好') == 9  # 5 ASCII + 4 CJK = 9 cells
```
[VERIFIED: executed on Python 3.12.3 + rich 13.7.1]

### Streaming Timing
```python
# Source: measured on this machine (Linux/WSL2 6.6.87.2)
import time
# 15ms sleep: actual ~15.2ms — acceptable precision
# 40ms sleep: actual ~40-57ms — WSL2 timer resolution varies slightly
# Implication: use time.sleep(0.015) to time.sleep(0.040) as specified in DISP-02
```
[VERIFIED: measured via time.monotonic()]

### pyproject.toml with src-layout (setuptools 68.1.2)
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "claude-legado"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["rich>=13.7"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```
[ASSUMED] — Standard modern pyproject.toml format; setuptools src-layout support confirmed in setuptools 61+ docs.

### Claude Code Skill File (`novel.md`)
```markdown
---
name: novel
description: Read Chinese web novels. Use when user invokes /novel or asks to read a novel.
argument-hint: "[next|prev|search <query>|toc|shelf|use <path>]"
disable-model-invocation: true
allowed-tools: Bash(python *:*)
---

Run this bash command and output the result exactly as-is without adding any commentary:

```bash
cd "$(git -C "$HOME" rev-parse --show-toplevel 2>/dev/null || echo .)" && PYTHONPATH=src python -m novel $ARGUMENTS
```
```
[VERIFIED: skill file frontmatter format from official Claude Code docs at code.claude.com/docs/en/slash-commands]

**Note:** The path resolution in the bash block above is illustrative. For a project-scoped skill, the simpler `PYTHONPATH=src python -m novel $ARGUMENTS` works because Claude Code opens in the project root. The planner should confirm the cleanest invocation pattern.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.claude/commands/*.md` | `.claude/skills/<name>/SKILL.md` | 2025 | Both still work; skills add frontmatter + supporting files; commands are still fully supported |
| `setup.py` | `pyproject.toml` + PEP 517 build backend | Python 3.10+ era | setuptools 68 supports pyproject.toml natively without setup.py |
| `sys.stdout.write` + ANSI codes | `rich.console.Console` | 2020+ | Rich handles terminal capability detection; use raw stdout only for character streaming |

**Deprecated/outdated:**
- `setup.py` alone: replaced by `pyproject.toml`; use setuptools backend with `[tool.setuptools.packages.find] where = ["src"]`
- Separate `rich.Live` context for streaming: `Live` is for updating in-place (progress bars, spinners); character-streaming does NOT use Live — it uses regular stdout with no context manager

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Atomic write via `Path.tmp` + `Path.replace()` prevents state corruption | Architecture Patterns / State Pattern | Low — POSIX `rename()` is atomic; Path.replace() delegates to it |
| A2 | `PYTHONPATH=src python -m novel` works without `pip install -e .` | Common Pitfalls / Pitfall 3 | Medium — if `src/novel/__init__.py` is missing, module not found; fixable in Wave 0 |
| A3 | pyproject.toml with setuptools `find.where = ["src"]` correctly discovers `src/novel/` | Standard Stack | Low — well-documented setuptools feature; setuptools 68.1.2 confirmed installed |
| A4 | Claude Code passes empty `$ARGUMENTS` (not an error) when `/novel` invoked with no args | Architecture Patterns / Dispatcher | Medium — could be `None`, empty string, or absent; guard with `args = sys.argv[1:]` handles all cases |
| A5 | Rich 13.7.1 (installed) vs 14.3.3 (latest) — all Phase 1 features present in 13.7.1 | Standard Stack | Low — CJK cell_len, Console.print, markup= all present; verified by running tests above |

## Open Questions

1. **Skill file path for `python -m novel`**
   - What we know: Claude Code opens in the project root; `python -m novel` requires `novel` to be importable; src-layout requires either `pip install -e .` or `PYTHONPATH=src`
   - What's unclear: Does the plan include a setup step (`pip install -e .`) as Wave 0, or does the skill file use `PYTHONPATH=src`?
   - Recommendation: Plan 01-01 should include `pyproject.toml` + `pip install -e .` as a Wave 0 setup step; cleaner than PYTHONPATH hacks and prepares for Phase 2+

2. **Fake chapter content generation**
   - What we know: D-07 requires >=500 CJK chars per chapter, 3 chapters, xianxia/wuxia genre
   - What's unclear: Should content be written by the implementer inline, or is there a specific source?
   - Recommendation: Implementer generates ~600-800 chars of plausible xianxia prose per chapter using LLM-generated or public-domain content; exact wording is Claude's Discretion (D-07)

3. **Reasoning preamble wording**
   - What we know: D-04 says "short italicized fake reasoning block"; D-specifics says `*正在准备章节内容...*` or `*Retrieving chapter content from source...*`; exact wording is Claude's Discretion
   - What's unclear: Chinese vs English? Vary per invocation?
   - Recommendation: Use a small list of 3–4 variants, randomly selected; mix Chinese and English for authenticity

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Package runtime | Yes | 3.12.3 | — |
| pip | Package installation | Yes | 26.0.1 | — |
| rich | Display engine | Yes | 13.7.1 (latest: 14.3.3) | — |
| pytest | Test suite | Yes | 9.0.2 | — |
| setuptools | pyproject.toml build | Yes | 68.1.2 | — |
| ~/.claude-legado/ | State persistence | Not yet created | — | Created on first run (mkdir parents=True exist_ok=True) |

[VERIFIED: all availability checks run via bash on 2026-04-07]

**Missing dependencies with no fallback:** None — all required tools are present.

**Missing dependencies with fallback:** `~/.claude-legado/` does not exist yet, but the package creates it on first run.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — see Wave 0 |
| Quick run command | `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -x -q` |
| Full suite command | `cd /home/ubwzwd/Code/claude_legado && pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SKILL-02 | `/novel` no args dispatches to stream current chapter | unit | `pytest tests/test_commands.py::test_default_dispatch -x` | Wave 0 |
| SKILL-03 | `/novel next` increments chapter index | unit | `pytest tests/test_commands.py::test_next_dispatch -x` | Wave 0 |
| SKILL-04 | `/novel prev` decrements chapter index | unit | `pytest tests/test_commands.py::test_prev_dispatch -x` | Wave 0 |
| SKILL-05..08 | Stub commands return string (not error) | unit | `pytest tests/test_commands.py::test_stub_commands -x` | Wave 0 |
| DISP-02 | char_delay returns correct range | unit | `pytest tests/test_display.py::test_char_delay -x` | Wave 0 |
| DISP-04 | CJK chars get double width | unit | `pytest tests/test_display.py::test_cjk_width -x` | Wave 0 |
| STATE-01 | save_state writes valid JSON to correct path | unit | `pytest tests/test_state.py::test_save_state -x` | Wave 0 |
| STATE-02 | load_state returns DEFAULT_STATE when file missing | unit | `pytest tests/test_state.py::test_load_state_missing -x` | Wave 0 |
| STATE-02 | load_state returns saved state when file exists | unit | `pytest tests/test_state.py::test_load_state_exists -x` | Wave 0 |
| STATE-03 | shelf.json created on init | unit | `pytest tests/test_state.py::test_shelf_init -x` | Wave 0 |
| DISP-01,03 | stream_text produces stdout output (not empty) | smoke | `pytest tests/test_display.py::test_stream_text_output -x` | Wave 0 |
| DISP-05 | Console does not use alternate screen | manual | n/a — visual check | manual-only |
| DISP-06,07 | Header and nav hints printed (captured stdout) | unit | `pytest tests/test_display.py::test_header_and_hints -x` | Wave 0 |

Note: DISP-01/DISP-03 streaming timing (the visual "indistinguishable from Claude" quality) is manual-only — automated tests verify the function runs and produces output but cannot validate subjective timing perception.

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/__init__.py` — package marker
- [ ] `tests/test_commands.py` — covers SKILL-02 through SKILL-08 dispatch
- [ ] `tests/test_display.py` — covers DISP-02, DISP-04, DISP-01/03 smoke, DISP-06/07
- [ ] `tests/test_state.py` — covers STATE-01 through STATE-04
- [ ] `tests/conftest.py` — shared fixture: temp directory for `~/.claude-legado/` (override `STATE_DIR` to a tmp path during tests)
- [ ] `pyproject.toml` — `[tool.pytest.ini_options]` block with `testpaths = ["tests"]`
- [ ] Package installation: `pip install -e .` — required before `pytest` can import `novel`

## Security Domain

> ASVS assessment: Phase 1 is a local CLI tool with no network access, no authentication, no user-generated content from untrusted sources (only hardcoded data), and no crypto operations.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not applicable — local tool, no auth |
| V3 Session Management | No | Not applicable — stateless per invocation |
| V4 Access Control | No | Not applicable — single-user local tool |
| V5 Input Validation | Partial | `sys.argv` parsing — validate command name against allowlist (already in dispatcher pattern) |
| V6 Cryptography | No | Not applicable — no crypto in Phase 1 |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed `state.json` (hand-edited or corrupted) | Tampering | `try/except json.JSONDecodeError` in `load_state()` — fallback to DEFAULT_STATE |
| Unexpected `$ARGUMENTS` value from skill file | Tampering | Allowlist dispatch: unknown commands fall through to default/stub, never exec'd |
| Path traversal via `use <path>` argument (Phase 1: stubbed) | Tampering | Stub returns fixed string — no file I/O performed on argument in Phase 1 |

No critical security findings for Phase 1. The primary concern (untrusted user input) is fully mitigated by the stubbed `use` command and allowlist dispatcher.

## Sources

### Primary (HIGH confidence)
- `rich.cells.cell_len` — verified by execution on Python 3.12.3 + rich 13.7.1
- `rich.console.Console` init signature — verified by `inspect.signature(Console.__init__)`
- `time.sleep` at 15ms precision — verified by measurement on this machine
- `sys.stdout.write` + flush approach — verified by Python 3.12 stdlib
- Claude Code slash command / skill format — [code.claude.com/docs/en/slash-commands](https://code.claude.com/docs/en/slash-commands) (fetched 2026-04-07)
- `pip index versions rich` — verified: 14.3.3 latest, 13.7.1 installed
- `pip index versions pytest` — verified: 9.0.2 installed and latest on this machine

### Secondary (MEDIUM confidence)
- pyproject.toml + setuptools src-layout — setuptools 68.1.2 installed; format based on PEP 517/518 standard
- Atomic file write via `Path.replace()` — POSIX standard; Python docs confirm rename semantics

### Tertiary (LOW confidence)
- None — all critical claims verified or from official sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified via pip, all APIs verified by execution
- Architecture: HIGH — patterns verified against official Claude Code docs and Python stdlib
- Pitfalls: MEDIUM — identified from code patterns and verified where testable; some are ASSUMED from common Python CLI experience
- Validation architecture: HIGH — pytest confirmed installed, test file structure follows standard pytest conventions

**Research date:** 2026-04-07
**Valid until:** 2026-07-07 (stable stack; Rich and pytest are slow-moving; Claude Code skill format from official docs)
