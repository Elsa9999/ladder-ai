# Prompt For Antigravity

Use this when asking another AI agent to maintain or extend the XML pattern
library.

```text
Work only on the XML pattern library first. Do not return to the contest PLC
program until the library tasks below are complete.

Repo:
D:\AI_Agent_PLC_LADDER_ONLY

Library root:
D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library

Goal:
Make the TIA Portal V18 SimaticML pattern library reliable for future LAD XML
generation. Agents must reuse library patterns and must not invent Siemens XML.

Tasks:
1. Read README.md, AGENT_GUIDE.md, CATALOG.md, and MISSING_PATTERNS.md.
2. Validate the existing library:
   python examples\TIA_V18_XML_Pattern_Library\tools\validate_patterns.py
   python examples\TIA_V18_XML_Pattern_Library\tools\build_catalog.py
3. Keep the existing 37 patterns passing.
4. If adding new patterns, only add patterns from known-good TIA Portal V18
   exports or generated XML that has passed import/compile in TIA.
5. For every new pattern folder, include:
   - pattern.xml
   - manifest.json
   - README.md
   - compile_notes.md or TODO.md
6. Update CATALOG.md and manifest.json after changes.
7. For PID patterns in this workspace, enforce PID_Compact Version="1.2" and
   the sRet.i_Mode rule: move 3 when Auto/Enable is true, move 0 when false.
8. Keep GET/PUT out of new patterns unless placed under a clearly marked
   legacy/deprecated folder.

Acceptance:
- validate_patterns.py exits 0
- build_catalog.py exits 0
- CATALOG.md lists every pattern
- manifest.json patterns_count matches the real number of pattern folders
- No broken XML files
```
