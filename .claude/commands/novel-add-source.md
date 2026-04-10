---
name: novel-add-source
description: Ingest a new Legado book source by providing its JSON content or a URL.
argument-hint: "<json-or-url>"
---

Run this bash command. It generates a formatted response for the user. Do not repeat the output in your response.

```bash
PYTHONPATH=src python3 -m novel add-source "$ARGUMENTS"
```
