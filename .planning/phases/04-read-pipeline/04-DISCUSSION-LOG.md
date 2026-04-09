# Phase 04: Read Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 04-Read Pipeline
**Areas discussed:** Search & Add Workflow, Book Info Display, TOC Handling, Content Fetching & Navigation, Shelf Management, Search Results Formatting, Missing Data Fallback, Save Progress Triggers

---

## Search & Add Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| 1a | `/novel search` saves cache; `/novel add <index>` picks it | ✓ |
| 1b | List results with a dedicated `uid` you copy-paste into `/novel add <uid>` | |

**User's choice:** 1a
**Notes:** Clean separation. Keeps commands simple without needing a TUI interaction.

---

## Book Info Display

| Option | Description | Selected |
|--------|-------------|----------|
| 2a | Shown automatically when the book is added to the shelf | |
| 2b | Handled via a separate `/novel info` command | ✓ |

**User's choice:** 2b
**Notes:** Less noise when just adding books.

---

## TOC Display limits

| Option | Description | Selected |
|--------|-------------|----------|
| 3a | Truncate at 50, require `--all` flag to show the rest | |
| 3b | Paginate via `/novel toc <page_number>` | ✓ |

**User's choice:** 3b
**Notes:** Graceful handling for novels with thousands of chapters.

---

## Content Fetching & Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| 4a | Fetch strictly on-demand (simpler, slightly slower) | ✓ |
| 4b | Pre-fetch the next chapter in the background while reading | |

**User's choice:** 4a
**Notes:** Matches the sync-client stack decisions and constraints.

---

## Shelf Management

| Option | Description | Selected |
|--------|-------------|----------|
| 5a | `/novel shelf` lists books with index IDs; `/novel read <id>` makes it active | ✓ |
| 5b | `/novel shelf` lists books; `/novel shelf <id>` implies making it active | |

**User's choice:** 5a
**Notes:** Explicit read command is clearer.

---

## Search Results Formatting

| Option | Description | Selected |
|--------|-------------|----------|
| 1a | Compact: Just `[index] Title - Author` | |
| 1b | Detailed: Include the latest chapter or update time | |
| 1c | Other | ✓ |

**User's choice:** Display `[index] Title - Author - name of the book source`
**Notes:** Shows required disambiguation since we might be searching across different sources in V2, or just to know which source we used.

---

## Missing Data Fallback

| Option | Description | Selected |
|--------|-------------|----------|
| 2a | Display a clear placeholder like `[No intro extracted]` | ✓ |
| 2b | Skip the field silently | |

**User's choice:** 2a
**Notes:** Makes it clear that data extraction failed, rather than the book not having an intro.

---

## Save Progress Triggers

| Option | Description | Selected |
|--------|-------------|----------|
| 3a | Before streaming starts (if Ctrl+C, they land on current/new chapter) | ✓ |
| 3b | After streaming finishes (if Ctrl+C mid-way, they resume from previous chapter layout) | |

**User's choice:** 3a
**Notes:** Optimizes for standard quick interruptions.

---

## Deferred Ideas
None
