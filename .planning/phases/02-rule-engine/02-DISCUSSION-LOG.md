# Phase 2: Rule Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion.

**Date:** 2026-04-07
**Phase:** 02-rule-engine
**Mode:** discuss
**Areas analyzed:** quickjs binding, Rule API shape, Test fixture strategy, Rule failure behavior

## Assumptions Presented

### Gray Areas Identified

| Area | Description |
|------|-------------|
| quickjs binding | Which Python quickjs package — `quickjs` PyPI vs `python-quickjs` vs defer JS to Phase 3 |
| Rule API shape | Single evaluate() function vs RuleEngine class vs BookSource-aware evaluator |
| Test fixture strategy | Synthetic minimal fixtures vs real community book source vs both |
| Rule failure behavior | Raise RuleError vs return empty string vs return Optional[str] |

## Corrections Made

No corrections — all recommended options confirmed.

### quickjs binding
- **Presented:** `quickjs` PyPI package (Recommended)
- **User chose:** `quickjs` PyPI package

### Rule API shape
- **Presented:** Single `evaluate()` function (Recommended)
- **User chose:** Single `evaluate()` function

### Test fixture strategy
- **Presented:** Synthetic minimal fixtures (Recommended)
- **User chose:** Synthetic minimal fixtures

### Rule failure behavior
- **Presented:** Raise `RuleError` (Recommended)
- **User chose:** Raise `RuleError`

## Prior Context Applied

From Phase 1 decisions:
- `src/novel/` src-layout — rule engine lands at `src/novel/rules/`
- No interactive stdin — all rule evaluation must be non-interactive
- Atomic write pattern established in `state.py` — available as reference

From STATE.md accumulated context:
- `java.ajax()` sync-in-JS flagged HIGH risk — resolved: stub with NotImplementedError in Phase 2, finalize in Phase 3
- 笔趣阁 domain instability flagged — not relevant to Phase 2 (no HTTP)
