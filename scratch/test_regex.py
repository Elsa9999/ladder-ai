# -*- coding: utf-8 -*-
import re

line1 = '                    f\'<Symbol>{ "".join(["<Component Name=\\"" + x + "\\" />" for x in comp[1].split(".")]) }</Symbol>\'\n'
line2 = '        comp_str = "".join([f\'<Component Name=\"{x}\" />\' for x in value_str.split(\".\")])'

# Let's write the regex to match both
# Pattern for double quote: "".join(["<Component Name=\"" + x + "\" />" for x in comp[1].split(".")])
# In line1, the pattern is: "".join(["<Component Name=\\"" + x + "\\" />" for x in comp[1].split(".")])
# Let's match the inner part: <Component Name=...
# We can match: "".join([<SOMETHING> for x in EXPR.split(".")])
# Regex:
pattern = r'""\.join\(\s*\[\s*(?:"<Component Name=\\\\" \+ x \+ \\\\" />"|f?\'<Component Name="\{x\}" />\')\s*for\s+x\s+in\s+(.*?)\.split\((?:"\."|\'\.\')\)\s*\]\s*\)'

print('Pattern matches line1:', bool(re.search(pattern, line1)))
print('Pattern matches line2:', bool(re.search(pattern, line2)))

# If we simplify the regex:
# We just match: "".join([<ANYTHING> for x in <EXPR>.split(".")])
# This is much simpler and extremely robust!
simple_pattern = r'""\.join\(\s*\[\s*.*?for\s+x\s+in\s+(.*?)\.split\((?:"\."|\'\.\')\)\s*\]\s*\)'
print('Simple Pattern matches line1:', bool(re.search(simple_pattern, line1)))
print('Simple Pattern matches line2:', bool(re.search(simple_pattern, line2)))
if re.search(simple_pattern, line1):
    print('Substituted line1:', re.sub(simple_pattern, r'format_symbol_path(\1)', line1).strip())
