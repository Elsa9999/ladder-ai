import os
import re
import xml.etree.ElementTree as ET

screens_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
tag_table_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Tags\Default tag table.xml"

# 1. Parse existing tags in Default Tag Table
existing_tags = set()
if os.path.exists(tag_table_xml):
    try:
        with open(tag_table_xml, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find all HMI.Tag.Tag names using regex for safety with custom namespaces
        tag_blocks = re.findall(r'<Hmi\.Tag\.Tag[^>]*>.*?</Hmi\.Tag\.Tag>', content, re.DOTALL)
        for block in tag_blocks:
            name_match = re.search(r'<Name>([^<]+)</Name>', block)
            if name_match:
                existing_tags.add(name_match.group(1))
    except Exception as e:
        print(f"Error parsing tag table: {e}")

print(f"Number of existing HMI tags: {len(existing_tags)}")

# 2. Scan HMI Screens for references to tags
referenced_tags = set()
if os.path.exists(screens_dir):
    for filename in os.listdir(screens_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(screens_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Regex for <Tag TargetID="@OpenLink">\s*<Name>([^<]+)</Name>
                tag_refs = re.findall(r'<Tag\s+TargetID="[^"]+">\s*<Name>([^<]+)</Name>', content, re.DOTALL)
                for t in tag_refs:
                    referenced_tags.add(t)
                
                # Also find general Tag references in associations
                tags = re.findall(r'Associate\s+Name="Tag"\s+Type="Association"\s+TargetID="[^"]+"\s+TargetName="([^"]+)"', content)
                for t in tags:
                    referenced_tags.add(t)
            except Exception as e:
                pass

print(f"Number of referenced HMI tags in screens: {len(referenced_tags)}")
print("\nHMI tags referenced in screens:")
for tag in sorted(list(referenced_tags)):
    status = "[Exists]" if tag in existing_tags else "[MISSING]"
    print(f"  {status} {tag}")
