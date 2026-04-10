---
status: testing
phase: 05-polish
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md]
started: 2026-04-10T17:59:00Z
updated: 2026-04-10T17:59:00Z
---

## Current Test

number: 3
name: Bookshelf Progress
expected: |
  Add a book to the shelf. Read at least one chapter.
  Run `/novel shelf`.
  The output should show the book title, author, and progress (e.g., "Chapter 1 / 100" or similar).
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: |
  Kill any running process. Run `/novel shelf`. 
  It should show "Reading Shelf" preamble and then a clear message about the shelf state without Python tracebacks.
result: pass

### 2. Claude Error Camouflage
expected: |
  Try to use a non-existent source: `/novel use ./missing.json`.
  The error should be displayed in *italic dim* formatting (simulating Claude's internal thinking style) and should NOT leak a Python stack trace.
result: pass

### 3. Bookshelf Progress
expected: |
  Add a book to the shelf. Read at least one chapter.
  Run `/novel shelf`.
  The output should show the book title, author, and progress (e.g., "Chapter 1 / 100" or similar).
result: [pending]

### 4. TOC Active Marker
expected: |
  Run `/novel toc`.
  The currently active chapter should be highlighted with a marker (e.g., `->`).
result: [pending]

### 5. README Installation Verification
expected: |
  Follow the README "Setup" instructions.
  The commands should work on a standard Linux environment.
result: issue
reported: "The slash command in .claude/commands/novel.md uses 'python', but the system only has 'python3' available, leading to Exit code 127."
severity: major

## Summary

total: 5
passed: 2
issues: 1
pending: 2
skipped: 0

## Gaps

- truth: "The commands should work on a standard Linux environment."
  status: failed
  reason: "User reported: /bin/bash: line 1: python: command not found (system has python3)"
  severity: major
  test: 5
  artifacts: []
  missing: []
