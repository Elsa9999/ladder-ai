# Agent Guide

Use this guide when an AI agent generates TIA Portal V18 LAD XML in this repo.

## Workflow

1. Read `CATALOG.md`.
2. Pick the smallest pattern that matches the requested instruction.
3. Read that pattern folder:
   - `pattern.xml`
   - `manifest.json`
   - `compile_notes.md`
4. Replace placeholders with real tag names, DB names, or constants.
5. Generate the final block XML.
6. Run the project validator/import-set validator for the target project.
7. If TIA rejects the XML, export a working manual block from TIA and normalize
   that export back into this library.

## Hard Rules

- Never invent XML for a Siemens instruction that is not represented here.
- Do not mix optimized DB assumptions with Modbus holding-register layouts.
  Modbus holding register DBs must stay Standard/Non-Optimized when byte/word
  alignment matters.
- Keep PLC-to-PLC communication on Modbus TCP for the current contest project.
- Use `MB_CLIENT` and `MB_SERVER` patterns for Modbus TCP.
- Use `MB_COMM_LOAD` and `MB_MASTER` patterns for Modbus RTU/VFD style work.
- Avoid GET/PUT for new designs unless the user explicitly asks for legacy
  comparison.
- Hardware settings such as clock memory, system memory, PROFINET topology, and
  HMI screen binding are not guaranteed by block XML alone. Use a seed TIA
  project or manual setup for those.

## PID Rule For This Workspace

Known-good PID style:

- `PID_Compact` instruction version: `1.2`
- Instance DB: technology-object instance, for example `AI_PID_Compact_1`
- Auto mode:
  - if enable/auto is true and `instance.sRet.i_Mode <> 3`, move `3` into
    `instance.sRet.i_Mode`
  - if enable/auto is false and `instance.sRet.i_Mode <> 0`, move `0` into
    `instance.sRet.i_Mode`
- Keep `ManualEnable` as the HMI/manual input; do not confuse it with
  `sRet.i_Mode`.

## Missing Pattern Policy

When the exact pattern is missing:

1. Add it to `MISSING_PATTERNS.md`.
2. Build the logic manually in a small TIA Portal V18 sample project.
3. Export using the repo Openness exporter.
4. Normalize placeholders.
5. Add `pattern.xml`, `manifest.json`, `README.md`, and `compile_notes.md`.
6. Run validation and update `CATALOG.md`.
