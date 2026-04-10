# claude-legado

Read Chinese web novels in the terminal — disguised as Claude AI output.

[Switch to Chinese version (中文版)](README.md)

claude-legado streams novel text character-by-character with variable delays that mimic natural LLM token generation, making it look like Claude is "thinking" and then producing a response. It uses [Legado](https://github.com/gedoor/legado) book-source rule files (`.json`) to fetch content from web novel sites.

## Features

- **Claude camouflage** — Output streams with a fake "thinking" preamble and realistic typing delays, burst chunks, and punctuation pauses so it looks like AI-generated text.
- **Legado-compatible rule engine** — Supports CSS, JSONPath, XPath, JS, and regex rules from Legado book-source JSON files.
- **Full reading pipeline** — Search → add to shelf → browse TOC → read chapters with `/novel next` and `/novel prev`.
- **Progress tracking** — Remembers your position per book. Shelf shows chapter counts; TOC highlights the active chapter.
- **Graceful errors** — Failures are printed in Claude's italic "thinking" style instead of stack traces.

## Requirements

- Python 3.12+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (for the `/novel` slash-command integration)

## Setup

```bash
# Clone the repository
git clone <repo-url> && cd claude_legado

# Create a virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The project registers a suite of Claude Code slash-commands automatically via `.claude/commands/`, so after installation you can use commands like `/novel-search` and `/novel-shelf` directly inside Claude Code.

## Quick Start

### 1. Add/Load a book source

You can ingest a Legado-format book-source JSON directly:

```
/novel-add-source https://example.com/source.json
```

Or just paste the JSON content if you have it. This stores and activates the source. You can list all sources with `/novel-sources`.

### 2. Search for a novel

```
/novel-search 斗破苍穹
```

### 3. Add a book to your shelf

```
/novel-add 1
```

### 4. Select a book to read

```
/novel-read 1
```

### 5. Browse table of contents

```
/novel-toc
```

The current chapter is marked with `->`.

### 6. Read

```
/novel          # Read the current chapter
/novel next     # Next chapter
/novel prev     # Previous chapter
```

Text streams with Claude-style delays and a "thinking" preamble.

## Other Commands

| Command | Description |
|---------|-------------|
| `/novel-shelf` | List books on your shelf with reading progress |
| `/novel-info` | Show details for the active book |
| `/novel-toc <page>` | Show a specific page of the TOC |
| `/novel-sources` | List all managed book sources |
| `/novel-use <index>` | Switch active source by index |

## How It Works

1. **Rule engine** — Legado source files define rules (CSS selectors, JSONPath expressions, XPath, JavaScript snippets, or regex) that extract book lists, chapter URLs, and content from HTML/JSON responses.
2. **HTTP transport** — Fetches pages with custom headers/cookies from the source config, auto-detecting GBK encoding and converting to UTF-8.
3. **Display engine** — Streams text character-by-character with randomized delays (15–40ms base, 60ms clause pauses, 150ms sentence pauses) and occasional burst chunks of 8–15 characters.
4. **State persistence** — Reading state lives in `~/.claude-legado/state.json`; the bookshelf in `shelf.json`; sources in `sources/`.

## Running Without Claude Code

You can also run commands directly:

```bash
PYTHONPATH=src python3 -m novel novel-sources
PYTHONPATH=src python3 -m novel novel-search "Title"
PYTHONPATH=src python3 -m novel
```

## License

MIT
