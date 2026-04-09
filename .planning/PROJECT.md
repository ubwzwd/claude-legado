# claude-legado

## What This Is

A Claude Code skill (`/novel`) that lets you read Chinese web novels at work while looking like you're using Claude Code. Novel content streams out character-by-character mimicking Claude's AI response style — from the outside it looks like you're in a normal AI coding session. Compatible with legado's book source JSON format, giving access to thousands of community-maintained novel scrapers.

## Core Value

Reads novels through any legado-compatible book source, displayed as convincing fake Claude output — indistinguishable from real AI work at a glance.

## Requirements

### Validated

- [x] Load and parse legado book source JSON format (书源) — Validated in Phase 2
- [x] HTTP transport with custom headers, GBK encoding, cookie support — Validated in Phase 3
- [x] `/novel use <source.json>` loads and stores book sources — Validated in Phase 3
- [x] Multi-page TOC/content pagination — Validated in Phase 3

### Active

- [ ] `/novel` skill that triggers from Claude Code session
- [ ] Search for books using a loaded book source
- [ ] Add found books to a local library (bookshelf)
- [ ] Resume reading from last saved position automatically
- [ ] Stream chapter content character-by-character, styled as Claude AI response
- [ ] Keyboard shortcuts: next page, prev page, jump chapter, quit
- [ ] Load and parse legado book source JSON format (书源)
- [ ] Save reading progress locally (book + chapter + position)

### Out of Scope

- Android/Kotlin code from legado — only reuse the book source JSON format spec
- Real-time sync with legado mobile app — standalone CLI tool
- Paid content or DRM-protected sources — only free web novel sources
- Audio/TTS reading — visual terminal only
- Social features (ratings, reviews, sharing) — personal reading tool

## Context

- **Inspiration**: [legado](https://github.com/gedoor/legado) — popular open-source Android novel reader with a powerful community book source ecosystem (数千个书源)
- **Book source format**: legado's 书源 are JSON files describing how to scrape a novel website — search rules, chapter list rules, content rules. Community maintains thousands of them.
- **Camouflage mechanism**: Content displayed using streaming (typewriter) output styled exactly like Claude Code's response format — fake prompt, fake thinking indicators, real novel text
- **Target user**: Developer who wants to read novels during work hours without getting caught
- **Platform**: Claude Code CLI skill (invoked via `/novel` in a Claude Code session)

## Constraints

- **Format compatibility**: Must parse legado book source JSON format — do not invent a new format
- **Claude Code skill system**: Must work as a `.claude/skills/` skill, triggered by `/novel`
- **No auth required**: Only support free, publicly accessible novel sources
- **Local storage**: Reading progress and library stored locally (e.g., `~/.claude-legado/`)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code skill (not standalone CLI) | User works inside Claude Code anyway; /novel blends into existing workflow | — Pending |
| Streaming output as camouflage | Most convincing disguise — looks exactly like Claude answering a question | — Pending |
| Reuse legado book source format | Thousands of community sources immediately available; no need to write scrapers | — Pending |
| New repo (not legado fork) | legado is Android/Kotlin; CLI is a different stack entirely. Credit legado in README | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-09 after Phase 03 completion*
