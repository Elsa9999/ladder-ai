import xml.etree.ElementTree as ET
import os
import re

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\PLC_Tags_B3to7.xml"

if not os.path.exists(path):
    print("File not found.")
    sys.exit(0)

tree = ET.parse(path)
root = tree.getroot()

tags = root.findall(".//SW.Tags.PlcTag")
print(f"Checking {len(tags)} tags for memory overlaps...")

# We parse addresses like %M12.0, %MW20, %MD100, %I0.0, %Q0.0
# We want to identify the byte range occupied by each tag
def parse_address(addr):
    if not addr:
        return None
    # match %M, %I, %Q, %IW, %QW, %MW, %ID, %QD, %MD
    m = re.match(r'%([MIQ])([BWD])?(\d+)(\.(\d+))?', addr, re.IGNORECASE)
    if not m:
        return None
    area = m.group(1).upper() # M, I, Q
    size_char = m.group(2) # None (bit), B, W, D
    byte_offset = int(m.group(3))
    bit_offset = int(m.group(5)) if m.group(5) is not None else 0
    
    if size_char == 'D' or size_char == 'd':
        length = 4
    elif size_char == 'W' or size_char == 'w':
        length = 2
    elif size_char == 'B' or size_char == 'b':
        length = 1
    else: # Bit
        length = 0.125 # 1 bit
        
    return area, byte_offset, bit_offset, length

used_ranges = []
for tag in tags:
    name_el = tag.find("AttributeList/Name")
    name = name_el.text if name_el is not None else ""
    logical_el = tag.find("AttributeList/LogicalAddress")
    address = logical_el.text if logical_el is not None else ""
    
    parsed = parse_address(address)
    if parsed:
        area, byte_offset, bit_offset, length = parsed
        used_ranges.append((name, address, area, byte_offset, bit_offset, length))

# Check overlaps
overlaps = []
for i in range(len(used_ranges)):
    for j in range(i+1, len(used_ranges)):
        name1, addr1, area1, byte1, bit1, len1 = used_ranges[i]
        name2, addr2, area2, byte2, bit2, len2 = used_ranges[j]
        
        if area1 != area2:
            continue
            
        # check overlap
        # for simplicity, calculate start and end in bits
        start1 = byte1 * 8 + bit1
        end1 = start1 + (len1 * 8 if len1 >= 1 else 1)
        
        start2 = byte2 * 8 + bit2
        end2 = start2 + (len2 * 8 if len2 >= 1 else 1)
        
        if max(start1, start2) < min(end1, end2):
            overlaps.append((name1, addr1, name2, addr2))

print(f"Found {len(overlaps)} memory overlaps.")
for o in overlaps[:10]:
    print(f"Overlap: {o[0]} ({o[1]}) <-> {o[2]} ({o[3]})")
