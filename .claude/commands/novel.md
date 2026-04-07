---
name: novel
description: Read Chinese web novels. Use when user invokes /novel or asks to read a novel.
argument-hint: "[next|prev|search <query>|toc|shelf|use <path>]"
---

Run this bash command and output the result exactly as-is without adding any commentary:

```bash
PYTHONPATH=src python -m novel $ARGUMENTS
```
