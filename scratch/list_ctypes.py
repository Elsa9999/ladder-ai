# -*- coding: utf-8 -*-
import re

with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all patterns of ("CTYPE", ... or ('CTYPE', ...
ctypes = set(re.findall(r'\(\s*["\']([A-Z0-9_]+)["\']\s*,', content))
print("Single-arg/Tuple ctypes:", sorted(ctypes))

# Let's also look for tuples where the first item is a string
tuples = re.findall(r'\(\s*["\']([A-Z0-9_]+)["\']\s*,[^)]+\)', content)
print("Tuple-based ctypes:", sorted(set(tuples)))
