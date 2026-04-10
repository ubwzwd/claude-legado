# claude-legado

Read Chinese web novels in the terminal — disguised as Claude AI output.

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
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The project registers as a Claude Code slash-command automatically via `.claude/commands/novel.md`, so after installation you can use `/novel` directly inside Claude Code.

## Quick Start

### 1. Load a book source

You need a Legado-format book-source JSON file. These are widely shared in Chinese novel-reading communities.

```
/novel use ./my_source.json
```

This copies the source into `~/.claude-legado/sources/` and sets it as the active source.

### 2. Search for a novel

```
/novel search 斗破苍穹
```

Results are displayed as a numbered list.

### 3. Add a book to your shelf

```
/novel add 1
```

Adds the first search result to your persistent shelf.

### 4. Select a book to read

```
/novel read 1
```

Sets the first book on your shelf as the active book.

### 5. Fetch the table of contents

```
/novel toc
```

Displays chapters in paginated form. The current chapter is marked with `->`.

### 6. Read

```
/novel          # Read the current chapter
/novel next     # Next chapter
/novel prev     # Previous chapter
```

Text streams to the terminal with Claude-style delays, complete with a "thinking" preamble and chapter headers.

## Other Commands

| Command | Description |
|---------|-------------|
| `/novel shelf` | List books on your shelf with reading progress |
| `/novel info` | Show details for the active book |
| `/novel toc <page>` | Show a specific page of the table of contents |

## How It Works

1. **Rule engine** — Legado source files define rules (CSS selectors, JSONPath expressions, XPath, JavaScript snippets, or regex) that extract book lists, chapter URLs, and content from HTML/JSON responses.
2. **HTTP transport** — Fetches pages with custom headers/cookies from the source config, auto-detecting GBK encoding and converting to UTF-8.
3. **Display engine** — Streams text character-by-character with randomized delays (15–40ms base, 60ms clause pauses, 150ms sentence pauses) and occasional burst chunks of 8–15 characters.
4. **State persistence** — Reading state lives in `~/.claude-legado/state.json`; the bookshelf in `shelf.json`; sources in `sources/`.

## Running Without Claude Code

You can also run commands directly:

```bash
PYTHONPATH=src python -m novel use ./my_source.json
PYTHONPATH=src python -m novel search "Title"
PYTHONPATH=src python -m novel next
```

## License

MIT
