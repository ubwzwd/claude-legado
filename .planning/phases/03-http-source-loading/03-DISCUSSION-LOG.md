# Phase 3: HTTP + Source Loading - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-08
**Phase:** 03-http-source-loading
**Mode:** discuss
**Areas discussed:** java.ajax() wiring, /novel use UX, Encoding detection strategy, HTTP client choice

## Gray Areas Presented

| Area | Description |
|------|-------------|
| java.ajax() wiring | HIGH risk (STATE.md). JS rules call java.ajax(url) synchronously. Three strategies: wire direct, two-pass pre-fetch, or unsupported. |
| /novel use UX | Command is stubbed. What does success look like to the user? Minimal confirm, metadata display, or connectivity ping? |
| Encoding detection | GBK/GB2312 Chinese sites. Detection strategy: Content-Type header → chardet → UTF-8? Always chardet? Try-UTF8-fallback-GBK? |
| HTTP client | httpx (PROJECT.md stack) vs requests. pyproject.toml has no HTTP dep yet. |

## Decisions Made

### java.ajax() Wiring
- **Presented:** Wire real HTTP into callable (Recommended) / Pre-fetch injection two-pass / Unsupported
- **User chose:** Pre-fetch injection (two-pass)
- **Rationale:** Keep HTTP logic out of _js.py. First pass: recording stub captures ajax(url) calls. Second pass: fetch those URLs, inject results, re-run JS with real data.

### /novel use UX
- **Presented:** Confirm + source metadata (Recommended) / Confirm only / Confirm + connectivity ping
- **User chose:** Confirm + source metadata
- **Rationale:** Show source name, base URL, which rule fields are present, and stored path. No connectivity ping — offline-safe.

### Encoding Detection
- **Presented:** Header → chardet → UTF-8 (Recommended) / Always charset-normalizer / Try UTF-8 fallback GBK
- **User chose:** Header → chardet → UTF-8
- **Rationale:** Most robust — handles sites that lie about their encoding. chardet/charset-normalizer as fallback when Content-Type is absent or unreliable.

### HTTP Client
- **Presented:** httpx (Recommended) / requests
- **User chose:** httpx
- **Rationale:** Already in PROJECT.md stack, sync client matches existing code, charset-normalizer ships with it.
