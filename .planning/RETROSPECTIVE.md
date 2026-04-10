# Retrospective: v1.0 MVP

**Shipped:** 2026-04-10
**Phases:** 6 | **Plans:** 17

### What Was Built
A robust, disguised novel reader for Claude Code. Reuses the Legado ecosystem for source definitions (CSS/XPath/JS) while wrapping the experience in a character-by-character "typewriter" display that mimics Claude's own terminal output.

### What Worked
- **QuickJS Integration**: Using a real JS engine (QuickJS) instead of trying to manually parse Legado's complex JS rules allowed us to support almost all community book sources immediately.
- **Sync Architecture**: Keeping the core logic synchronous simplified error handling and state management for a CLI-first tool.
- **Rich Integration**: Using the Rich library's `Live` console for character-at-a-time streaming proved effective for the "camouflage" effect.

### What Was Inefficient
- **Command Duplication**: Initially, we struggled with Claude Code repeating the output of slash commands. The "Silent Agent" directive in the command definitions finally solved this, but it took several iterations during UAT.
- **Rules Package complexity**: The transition from hardcoded stubs to a fully dynamic evaluating engine was the steepest technical hurdle.

### Patterns Established
- **Silent Agent Pattern**: For slash commands that handle their own terminal UI, directing the agent to be silent ensures a native feel.
- **Camouflage Preamble**: Standardizing on the `*Claude is thinking...*` preamble for all commands maintains the persona.

### Key Lessons
- **User Discovery**: Slash commands are significantly more discoverable than deep subcommand structures for CLI skills.
- **Managed Sources**: Offloading source file management from the user to the tool (via `/novel-add-source`) drastically lowers the barrier to entry.
