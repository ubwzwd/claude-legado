# Phase 06: Command Deconstruction & Source Maintenance

Refactor the `/novel` command into specialized slash commands and implement a "managed source" system where the tool ingests and maintains Legado book sources from raw content or URLs.

## Success Criteria

1.  Multiple top-level lash commands registered (`/novel-shelf`, `/novel-search`, `/novel-read`, `/novel-toc`, `/novel-info`, `/novel-sources`, `/novel-add-source`).
2.  `/novel-add-source` allows adding a source by pasting LEGADO JSON or a URL.
3.  Sources added via the CLI are stored in `~/.claude-legado/sources/` and named after the `bookSourceName`.
4.  All usage examples in `README.md` are updated to reflect the new command structure.

## Plans

- [ ] 06-01: Split slash commands — implement multiple `.md` files in `.claude/commands/`, update `commands.py` to route correctly.
- [ ] 06-02: Source maintenance system — implement `novel-add-source` and `novel-sources` logic with JSON/URL ingestion.
- [ ] 06-03: Documentation update — README and inline hints.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 6. Command Deconstruction | 0/3 | Not started | - |
