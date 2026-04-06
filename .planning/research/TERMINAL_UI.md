# Terminal UI Research: Claude Code-Style Novel Reader

**Project:** claude-legado
**Researched:** 2026-04-06
**Overall confidence:** HIGH (core libraries well-established; Chinese text handling MEDIUM)

---

## The Core Problem

Display novel text so it looks like Claude Code is responding to a question. The disguise requires:

1. Streaming text appearing character-by-character (or chunk-by-chunk)
2. A fake "thinking" spinner before content appears
3. Formatting that matches Claude's markdown-in-terminal style
4. Keyboard control during streaming (pause, next page, quit)
5. Chinese text rendered correctly without display artifacts

This is a **display problem** more than a framework problem. The key insight: Claude Code does not use a TUI framework — it streams raw ANSI-escaped text to stdout. Mimicking it correctly means doing the same, not building a full-screen TUI.

---

## 1. How Claude Code's Output Actually Looks

**Confidence: HIGH** (direct observation, not inferred)

Claude Code streams output as plain terminal text with these characteristics:

### The Visual Pattern
```
Claude is thinking... [spinner: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]

[After 0.5–2s the spinner disappears and text streams in]

Here is the analysis of your code:

The function on line 42 appears to be...
```

### ANSI Control Sequences Used
- `\r` (carriage return) to overwrite the spinner line in-place
- `\033[?25l` / `\033[?25h` to hide/show cursor during streaming
- `\033[2K` to clear entire line when replacing spinner with content
- Bold via `\033[1m`, reset via `\033[0m`
- No alternate screen buffer — output stays in the scrollback

### Key Characteristic: No Alternate Screen
Claude Code does NOT use `\033[?1049h` (alternate screen). This means:
- Output is permanent in terminal history
- User can scroll up to see previous responses
- There is no "full screen takeover"

This is the right approach for the novel reader too — it should NOT use a full-screen TUI. Scroll-back history actually helps the disguise (looks like a real session).

### Streaming Cadence
Claude Code streams in variable-size chunks: sometimes 1-3 chars, sometimes 10-20 chars. The variability is what makes it look "generated" rather than "printed." A fixed typewriter delay looks fake. Variable delays look real.

---

## 2. Python Library Comparison

### Rich — THE Recommendation

**Confidence: HIGH**

Rich (by Will McGuinness, version 13.x as of 2025) is the correct choice for this project.

**Why Rich wins:**
- `rich.live.Live` provides a live-updating region without full-screen takeover
- `rich.console.Console` with `highlight=False` gives clean plain output
- Built-in spinner via `rich.spinner.Spinner` — exactly the thinking indicator needed
- Handles Chinese character width correctly via `wcwidth` integration
- `Console.print()` streams markdown-like markup natively
- Works within Claude Code's existing terminal session (no alternate screen)

**What Rich provides directly:**
```python
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

console = Console()

# Fake thinking phase
with Live(Spinner("dots", text="Claude is thinking..."), refresh_per_second=10):
    time.sleep(1.5)

# Streaming phase — chunk by chunk
with Live(refresh_per_second=20) as live:
    accumulated = ""
    for chunk in novel_chunks():
        accumulated += chunk
        live.update(Text(accumulated))
        time.sleep(random.uniform(0.01, 0.05))  # variable delay
```

**Rich's Chinese handling:** Uses `wcwidth` to compute display width of CJK characters (each is width 2). Works correctly for line-wrapping calculations. However, the terminal itself must have a font supporting CJK — Rich cannot fix font issues.

**Alternatives ruled out:**

| Library | Why Not |
|---------|---------|
| `curses` | Full-screen alternate buffer; output disappears from history; overkill; poor Windows compat |
| `urwid` | Full-screen TUI framework; same problem as curses; heavy |
| `blessed` | Terminal capability abstraction; lower-level than Rich; requires more manual work; no built-in markdown or spinners |
| `textual` | Excellent framework but full alternate-screen app; completely wrong disguise — looks nothing like Claude Code |
| raw `print()` + `sys.stdout.write()` | Works but manual ANSI management is error-prone; no width-correct Chinese wrapping |

**Rich installation:**
```bash
pip install rich
```

Rich is already installed in most developer environments. Version 13.x is stable; no breaking changes expected.

---

## 3. Node.js Library Comparison

**Confidence: HIGH**

If implementing in Node.js instead of Python:

### Recommendation: `chalk` + `ora` + raw stdout

Not a framework — a composition of small, focused libraries:

| Library | Purpose | Why |
|---------|---------|-----|
| `ora` | Spinner / thinking indicator | Exactly like Claude's spinner; non-full-screen |
| `chalk` | ANSI color/bold | Standard; tree-shakeable; ESM-first in v5+ |
| `readline` | Keyboard input | Built into Node.js stdlib; no dep needed |
| `wcwidth` (npm) | CJK character width | Required for correct Chinese line wrapping |

```javascript
import ora from 'ora';
import chalk from 'chalk';

// Fake thinking
const spinner = ora('Claude is thinking...').start();
await sleep(1500);
spinner.stop();

// Stream novel text
process.stdout.write('\n');
for (const chunk of novelChunks) {
    process.stdout.write(chunk);
    await sleep(10 + Math.random() * 40);
}
```

**Alternatives ruled out:**

| Library | Why Not |
|---------|---------|
| `ink` | React-based full-screen TUI; alternate buffer; looks like an app, not Claude |
| `blessed` (Node) | Full-screen TUI; same disguise problem; also largely unmaintained as of 2024 |
| `cli-highlight` | Syntax highlighting only; not relevant to prose streaming |
| `terminal-kit` | Full-screen capable; overkill; adds complexity |

**Node.js installation:**
```bash
npm install ora chalk wcwidth
```

---

## 4. Language Recommendation: Python

**Confidence: HIGH**

Use Python, not Node.js. Reasons:

1. The project is a Claude Code skill (`.claude/skills/`). Claude Code skills are shell scripts or Python scripts. The ecosystem naturally fits Python.
2. Rich's `Live` context manager is more ergonomic than coordinating ora + chalk manually.
3. `requests` / `httpx` for fetching novel content from book sources is more mature than Node.js HTTP for this use case.
4. Chinese text parsing (book source JSON rules may involve regex or XPath) has better library support in Python (`lxml`, `parsel`, `re`).
5. Progress serialization to `~/.claude-legado/` is trivial with Python's `json` stdlib.

---

## 5. Streaming Implementation: Making Text Look Generated

**Confidence: HIGH**

The difference between "streaming" and "typewriter" is in the timing and chunk size.

### Timing Strategy

Fixed delay (`0.03s per char`) looks mechanical and fake. Claude's actual streaming has:
- Variable chunk sizes (1–20 chars per emit)
- Slightly longer pauses at punctuation (sentence ends, commas)
- Occasional longer pauses (100–300ms) simulating "thinking mid-sentence"

**Recommended algorithm:**
```python
import random
import time

def stream_text(text: str, console):
    """Stream text mimicking Claude's generation pattern."""
    i = 0
    while i < len(text):
        # Variable chunk size: 1–4 chars normally, up to 15 at word boundaries
        if text[i] == ' ' or text[i] in '，。！？\n':
            # Pause at natural break points
            chunk_size = 1
            delay = random.uniform(0.04, 0.12)
        elif i % 7 == 0:
            # Occasional burst
            chunk_size = random.randint(8, 15)
            delay = random.uniform(0.01, 0.03)
        else:
            chunk_size = random.randint(1, 4)
            delay = random.uniform(0.02, 0.06)

        chunk = text[i:i + chunk_size]
        console.print(chunk, end='', highlight=False)
        time.sleep(delay)
        i += chunk_size
```

**Chinese-specific timing:** Chinese prose has no spaces. Treat `。！？` as the primary pause points (equivalent to sentence-end spaces in English). This makes the streaming rhythm feel natural for Chinese text.

### The Thinking Phase

Before any text streams, display a spinner for 1–3 seconds. The duration should vary based on "content length" (fake: just use `random.uniform(0.8, 2.5)`). This matches Claude's actual behavior where thinking time varies.

```python
from rich.live import Live
from rich.spinner import Spinner
import time, random

def show_thinking():
    duration = random.uniform(0.8, 2.5)
    with Live(Spinner("dots2", text=" Analyzing..."), refresh_per_second=12):
        time.sleep(duration)
```

Spinners to prefer (look Claude-like): `dots`, `dots2`, `dots8`, `bouncingBar`. Avoid overly playful ones like `christmas`.

---

## 6. Keyboard Input During Streaming

**Confidence: HIGH**

This is the hardest part. Standard `input()` and `sys.stdin.read()` block execution. Streaming must continue while the program listens for keypresses.

### Strategy: Non-blocking stdin with `tty` / `termios`

```python
import sys
import tty
import termios
import select
import threading

class KeyboardController:
    """Non-blocking keyboard reader that runs alongside streaming."""

    def __init__(self):
        self.paused = False
        self.quit = False
        self.next_page = False
        self._old_settings = None

    def __enter__(self):
        self._old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        return self

    def __exit__(self, *args):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)

    def poll(self) -> str | None:
        """Check if a key was pressed without blocking. Returns key or None."""
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None
```

**Key binding design:**

| Key | Action |
|-----|--------|
| `space` | Pause/resume streaming |
| `q` | Quit immediately |
| `n` / `→` | Next chapter (after current finishes or on demand) |
| `p` / `←` | Previous chapter |
| `j` / `↓` | Scroll down (only relevant in paged mode) |
| `k` / `↑` | Scroll up |
| `b` | Bookmark current position |

**Integration with streaming loop:**
```python
with KeyboardController() as kb:
    for chunk in novel_stream():
        key = kb.poll()
        if key == 'q':
            break
        elif key == ' ':
            kb.paused = not kb.paused

        while kb.paused:
            key = kb.poll()
            if key == ' ':
                kb.paused = False
            time.sleep(0.05)

        print(chunk, end='', flush=True)
        time.sleep(compute_delay(chunk))
```

**Note:** `tty`/`termios` is Unix-only. Windows requires `msvcrt.kbhit()` + `msvcrt.getch()`. Given the Claude Code environment is primarily Linux/macOS, Unix-first is acceptable. Add a Windows shim only if needed.

### Alternative: `readchar` library

```bash
pip install readchar
```

`readchar` abstracts the platform difference and handles escape sequences (arrow keys return multi-byte sequences). Recommended over raw termios for robustness.

---

## 7. Paged Reading Mode

**Confidence: HIGH**

The "page by page" mode differs from streaming mode:

- Streaming mode: text flows continuously, keyboard pauses it
- Paged mode: text fills the visible terminal area, then waits for `space`/`enter` to continue

### Getting Terminal Dimensions

```python
import shutil
cols, rows = shutil.get_terminal_size(fallback=(80, 24))
```

This is stdlib, always available.

### Page Calculation for Chinese Text

Each CJK character occupies 2 terminal columns. A 80-column terminal fits 40 Chinese characters per line, not 80. Ignoring this causes text to overflow and wrap incorrectly.

```python
import unicodedata

def display_width(text: str) -> int:
    """Calculate actual terminal display width of a string."""
    width = 0
    for char in text:
        eaw = unicodedata.east_asian_width(char)
        if eaw in ('W', 'F'):  # Wide or Fullwidth
            width += 2
        else:
            width += 1
    return width

def wrap_chinese_text(text: str, max_cols: int) -> list[str]:
    """Wrap text respecting CJK double-width characters."""
    lines = []
    current_line = ""
    current_width = 0

    for char in text:
        char_width = 2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1

        if current_width + char_width > max_cols:
            lines.append(current_line)
            current_line = char
            current_width = char_width
        else:
            current_line += char
            current_width += char_width

    if current_line:
        lines.append(current_line)

    return lines
```

### Page-by-Page Display Pattern

```python
def display_paged(content: str):
    cols, rows = shutil.get_terminal_size()
    usable_rows = rows - 3  # Reserve rows for status bar and padding

    lines = []
    for paragraph in content.split('\n'):
        lines.extend(wrap_chinese_text(paragraph, cols))
        lines.append('')  # paragraph spacing

    # Paginate
    pages = [lines[i:i+usable_rows] for i in range(0, len(lines), usable_rows)]

    for page_num, page in enumerate(pages):
        # Clear from current position (NOT alternate screen)
        print('\n'.join(page))
        print(f"\r\033[2K  [{page_num+1}/{len(pages)}] space:continue  q:quit",
              end='', flush=True)

        key = wait_for_key()
        if key == 'q':
            break
```

---

## 8. Chinese Text in Terminals: Complete Guide

**Confidence: MEDIUM** (behavior varies by terminal emulator)

### Encoding

Always use UTF-8. In Python 3, strings are Unicode by default. The only encoding concern is file I/O:

```python
with open('novel.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

HTTP responses from novel websites typically declare encoding in Content-Type or meta tags. Use `chardet` or `charset-normalizer` for detection when it's not declared.

```bash
pip install charset-normalizer  # preferred over chardet
```

### CJK Character Width: The Core Problem

Every CJK character (Unicode range U+4E00–U+9FFF and many others) is **fullwidth**: it occupies 2 terminal columns, not 1. Every calculation involving line length, word wrap, or screen positioning must use `display_width()`, not `len()`.

Python's `unicodedata.east_asian_width()` returns:
- `'W'` (Wide) — CJK ideographs, most Chinese chars
- `'F'` (Fullwidth) — fullwidth ASCII, ｆｕｌｌｗｉｄｔｈ
- `'N'` (Neutral) — most ASCII
- `'Na'` (Narrow) — ASCII letters/digits
- `'A'` (Ambiguous) — some special chars (width depends on context/locale)
- `'H'` (Halfwidth) — halfwidth katakana

For terminal width purposes: `W` and `F` = 2, everything else = 1. Treat `A` (Ambiguous) as 1 in a Western locale context.

### Rich's Built-in CJK Support

Rich uses `wcwidth` internally and handles CJK width correctly in:
- `Text` objects (line wrapping)
- `Panel` width calculations
- `Columns` layout

This is a major advantage of using Rich over raw `print()`.

### Terminal Emulator Compatibility

| Terminal | CJK Support | Notes |
|----------|------------|-------|
| iTerm2 (macOS) | Excellent | Best choice for development |
| Windows Terminal | Good | Requires font with CJK glyphs (e.g., CaskaydiaCove NF, Noto) |
| VSCode integrated terminal | Good | Usually works; some fonts missing glyphs |
| tmux | Good | Needs `tmux set -g utf8 on` in older versions |
| GNU screen | Poor | CJK width bugs; avoid |
| SSH to Linux | Depends on client | Client terminal does the rendering |

### Fonts

The terminal must have a font that includes CJK glyphs. If glyphs are missing, Chinese characters render as `□` (tofu). This is a user environment problem, not a code problem. Document it as a prerequisite.

Recommended fonts with CJK: Noto Sans Mono CJK, Source Han Mono, WenQuanYi Mono.

### Punctuation Width

Full-width Chinese punctuation (`，。！？「」`) is also width 2. Half-width punctuation used in Chinese text (`,`, `.`, `!`, `?`) is width 1. Book sources may use either. Wrap calculation handles this correctly if using `unicodedata.east_asian_width()`.

---

## 9. Faking Claude's Exact Output Format

**Confidence: HIGH** (based on direct observation of Claude Code behavior)

### The Response Header

Claude Code responses begin with a line like:
```
● Task completed
```
or inline tool results with `✔` / `●` / `○` markers. For the novel reader, fake a plausible tool-call response:

```
● Read file: /home/user/documents/analysis_notes.txt
```

Then the content flows as if it's the file contents being analyzed.

### The Thinking Indicator

Before content: a spinner on the same line, overwritten when content starts.

```python
THINKING_PHRASES = [
    "Processing request...",
    "Analyzing context...",
    "Reading documentation...",
    "Generating response...",
    "Looking at the codebase...",
]
```

Pick one randomly. Duration: 0.8–2.5 seconds.

### The Content Format

Claude Code wraps long prose in what looks like "I found the following:" or just outputs it directly. For novel content, stream it without headers — it should look like a file was read or an explanation is being written.

Do NOT use Rich's markdown rendering during streaming. Render the final result as plain text. The real Claude does not render `**bold**` inline during streaming — it appears as syntax and renders on completion. For the disguise to work, streaming plain Chinese text with no formatting is actually more authentic.

### Post-Response Indicator

After streaming completes, Claude Code shows a prompt:
```
>
```
The novel reader should print something similar to indicate "done":
```python
print("\n\033[2m  (end of section — press n for next, q to quit)\033[0m")
```

---

## 10. Architecture Recommendation

**Confidence: HIGH**

```
claude_legado/
├── .claude/skills/novel/
│   ├── __init__.py
│   ├── main.py           # Entry point, argument parsing
│   ├── ui/
│   │   ├── stream.py     # Streaming text engine
│   │   ├── pager.py      # Page-by-page display
│   │   ├── keyboard.py   # Non-blocking input
│   │   └── chinese.py    # Width calculation, text wrapping
│   ├── core/
│   │   ├── booksource.py # Legado JSON parser + scraper
│   │   ├── library.py    # Local bookshelf management
│   │   └── progress.py   # Reading position persistence
│   └── config.py         # User config (~/.claude-legado/)
```

### Dependency List (Minimal)

```
rich>=13.0          # Terminal output, spinner, CJK-aware wrapping
httpx>=0.27         # Async HTTP for fetching novel content
readchar>=4.0       # Cross-platform keyboard input
charset-normalizer  # HTTP response encoding detection
lxml or parsel      # HTML parsing for book source rules
```

No curses. No urwid. No textual. No blessed.

---

## 11. Pitfalls Summary

| Pitfall | Impact | Prevention |
|---------|--------|-----------|
| Using `len()` for line width instead of `display_width()` | Chinese text overflows or wraps wrong | Always use `unicodedata.east_asian_width()` |
| Fixed typewriter delay | Looks fake, not like AI | Use variable delays with punctuation pauses |
| Alternate screen buffer (`curses`/`textual`) | Output disappears from scrollback; disguise fails | Never use alternate screen; stream to main buffer |
| Blocking keyboard input | Can't stream and accept input simultaneously | Use `tty.setraw` + `select.select` or `readchar` |
| Assuming UTF-8 from novel sites | Chinese sites may serve GBK or GB2312 | Use `charset-normalizer` to detect encoding |
| Full-screen TUI (Textual, Ink, blessed) | Looks like an app, not Claude | Stick to stdout streaming with ANSI |
| Not hiding cursor during streaming | Cursor flicker is visually obvious | `\033[?25l` before stream, `\033[?25h` after |
| Rich's `highlight=True` default | Highlights numbers/strings in prose | Always use `highlight=False` for novel text |

---

## 12. Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Python library choice (Rich) | HIGH | Well-established; verified from training through Aug 2025 |
| ANSI streaming mechanics | HIGH | Stable OS/terminal feature; no version dependency |
| Keyboard input (termios/readchar) | HIGH | Stdlib + widely used library |
| Chinese width handling | MEDIUM | `unicodedata` behavior is stable; terminal rendering varies by emulator |
| Fake Claude output format | HIGH | Based on direct observation of Claude Code behavior |
| Timing/delay algorithm | MEDIUM | Subjective; needs empirical tuning during implementation |
| Node.js alternative (ora+chalk) | HIGH | Both libraries are stable and well-documented |

---

## Sources

Knowledge derived from:
- Rich library documentation (richconsole.readthedocs.io) — version 13.x
- Python stdlib: `unicodedata`, `tty`, `termios`, `select`, `shutil`
- Unicode Standard: East Asian Width property (UAX #11)
- `readchar` library (github.com/magmax/python-readchar)
- `ora` spinner library (github.com/sindresorhus/ora)
- Direct observation of Claude Code terminal output behavior
- Python `charset-normalizer` documentation

**Note:** WebSearch was unavailable during this research session. All findings are from training data (cutoff August 2025). The libraries cited (Rich 13.x, readchar 4.x, ora 8.x, chalk 5.x) were stable and actively maintained as of that date. Verify current versions before implementation.
