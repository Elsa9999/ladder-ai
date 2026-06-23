# TIA V18 SimaticML XML Pattern Library

This folder is the reusable XML pattern library for Siemens TIA Portal V18,
S7-1200, Ladder/SimaticML generation.

The goal is simple: agents should reuse known-good XML patterns instead of
guessing Siemens XML by hand. When a pattern is missing, create a TODO or export
the pattern from TIA Portal first.

## Current Contents

- `patterns/`: reusable pattern folders grouped by feature area.
- `CATALOG.md`: generated index of every pattern and its required tags/DBs.
- `AGENT_GUIDE.md`: rules for AI agents that generate or modify LAD XML.
- `MISSING_PATTERNS.md`: backlog of patterns still worth exporting.
- `tools/validate_patterns.py`: validates pattern folder structure and XML.
- `tools/build_catalog.py`: rebuilds `CATALOG.md` and updates root manifest.

## Use Rules

1. Check `CATALOG.md` before writing XML.
2. Copy the closest `pattern.xml` and replace placeholders such as
   `{{BOOL_IN}}`, `{{REAL_OUT}}`, or `{{DB_INSTANCE}}`.
3. Keep UIds unique inside the generated block.
4. Keep all required tags, DBs, instance DBs, and data types from the pattern
   manifest.
5. Do not create new Siemens instruction XML from memory. Export it from TIA
   Portal V18 first, then normalize it into this library.
6. Do not use GET/PUT for new PLC-to-PLC work. Keep GET/PUT only as legacy
   reference if it is ever added.
7. For PID in this workspace, prefer `PID_Compact` version `1.2` and add the
   `sRet.i_Mode` guard pattern: mode `3` when auto/enable is true, mode `0`
   when false.

## Validate

Run from the repository root:

```powershell
python examples\TIA_V18_XML_Pattern_Library\tools\validate_patterns.py
python examples\TIA_V18_XML_Pattern_Library\tools\build_catalog.py
```

Expected result: all pattern folders pass validation, and `manifest.json`
contains the current `patterns_count`.
