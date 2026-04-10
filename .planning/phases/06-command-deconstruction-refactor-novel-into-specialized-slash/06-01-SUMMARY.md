# Summary: Command Deconstruction (Backend & Entry Points)

Refactored the entry point logic to support multiple specialized slash commands.

## Accomplishments
- Refactored `src/novel/commands.py` `dispatch()` to handle specialized subcommands (`novel-shelf`, `novel-search`, etc.).
- Created specialized slash command definitions in `.claude/commands/`.
- Simplified the main `/novel` command to focus on reading and navigation.
