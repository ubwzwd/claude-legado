# claude-legado

## What This Is

A Claude Code skill (`/novel`) that lets you read Chinese web novels at work while looking like you're using Claude Code. Novel content streams out character-by-character mimicking Claude's AI response style — from the outside it looks like you're in a normal AI coding session. Compatible with legado's book source JSON format, giving access to thousands of community-maintained novel scrapers.

## Core Value

Reads novels through any legado-compatible book source, displayed as convincing fake Claude output — indistinguishable from real AI work at a glance.

## Requirements

### Validated

- [x] **Legado Support**: Parse book source JSON (CSS, XPath, JSONPath, JS) — v1.0
- [x] **HTTP Layer**: Transport with custom headers, GBK encoding, cookie support — v1.0
- [x] **Claude Skill**: Integration via `.claude/commands/` slash commands — v1.0
- [x] **Camouflage**: Character-by-character streaming with fake AI preamble — v1.0
- [x] **Library**: Bookshelf persistence and reading progress tracking — v1.0
- [x] **Discovery**: Book search and TOC navigation flows — v1.0
- [x] **Sources**: Managed source ingestion system (JSON/URL) — v1.0

### Active (Next Milestone: v1.1 - Security & Performance)

- [ ] **Configurable Speed**: Allow users to set streaming delay (slow/normal/fast)
- [ ] **Site-Specific Rules**: Add predefined "Gold Standard" sources for popular sites
- [ ] **Performance Audit**: Optimize QuickJS execution and TOC loading speeds
- [ ] **Security Review**: Validate source JS expressions against local resource access

### Out of Scope

- Android/Kotlin code from legado — only reuse the book source JSON format spec
- Real-time sync with legado mobile app — standalone CLI tool
- Paid content or DRM-protected sources — only free web novel sources
- Audio/TTS reading — visual terminal only
- Social features (ratings, reviews, sharing) — personal reading tool

- **Platform**: Claude Code CLI skill (invoked via `/novel` and `/novel-*` commands)
- **Tech Stack**: Python 3.10+, Rich (display), QuickJS (rule engine), Beautiful Soup (scraping)
- **Codebase**: ~1,800 LOC of synchronous, robust terminal logic
- **Camouflage**: Silent agent directive for slash commands ensures tool output flows naturally into the chat without duplication.

## Constraints

- **Format compatibility**: Must parse legado book source JSON format — do not invent a new format
- **Claude Code skill system**: Must work as a `.claude/skills/` skill, triggered by `/novel`
- **No auth required**: Only support free, publicly accessible novel sources
- **Local storage**: Reading progress and library stored locally (e.g., `~/.claude-legado/`)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code skill | User works inside Claude Code anyway; /novel blends into existing workflow | ✓ Good |
| Streaming output | Most convincing disguise — looks exactly like Claude answering a question | ✓ Good |
| Reuse legado format | Access to thousands of community sources immediately | ✓ Good |
| Silent agent directive | Prevents duplication of tool output in Claude Code chat | ✓ Good |
| Managed sources | Tool handles book source ingestion to protect user from manual file management | ✓ Good |

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
*Last updated: 2026-04-10 after v1.0 Milestone completion*
