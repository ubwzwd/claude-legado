# Phase 05: Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 05-polish
**Areas discussed:** Error Presentation, Shelf Information Density, TOC Navigation Marker, Out-of-the-box Experience

---

## Error Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Claude Disguise | Print a fake streaming Claude apology | ✓ |
| Standard CLI Error | Print a clean, readable error message without tracebacks, but drop the Claude disguise | |

**User's choice:** 1 (Claude Disguise)
**Notes:** User opted for the recommended option to preserve camouflage.

---

## Shelf Information Density

| Option | Description | Selected |
|--------|-------------|----------|
| The basics only | `[ID] Title - Author` (similar to search results) | |
| With progress | `[ID] Title - Author (Chapter 42 / 1000)` so you know where you left off at a glance | ✓ |

**User's choice:** 2 (With progress)
**Notes:** Selected the recommended detailed progress view.

---

## TOC Navigation Marker

| Option | Description | Selected |
|--------|-------------|----------|
| Current chapter marker | Highlight the active chapter (`-> [42] Chapter 42`) | ✓ |
| Plain list | Just a numbered list of chapters | |

**User's choice:** 1 (Current chapter marker)
**Notes:** User opted for clear active visualization within the TOC.

---

## Out-of-the-box Experience

| Option | Description | Selected |
|--------|-------------|----------|
| Include a default source | Ship a popular source JSON (like biquge) in the repo | |
| Require manual setup | Keep the repo clean; users must find their own source and run `/novel use <file>` | ✓ |

**User's choice:** 2 (Require manual setup)
**Notes:** Decided against shipping a predefined source, ensuring the repo doesn't contain legally questionable web scrapers by default.

---

## the agent's Discretion

None

## Deferred Ideas

None
