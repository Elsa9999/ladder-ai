import re

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\PLC_Tags_B3to7.xml"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace address for Timer_Sim_Pulse_Output
# <Name>Timer_Sim_Pulse_Output</Name> and its LogicalAddress
# Let's do a robust regex or string replacement
new_content = content
new_content = re.sub(
    r'(<LogicalAddress>%M)210\.0(</LogicalAddress>\s*<Name>Timer_Sim_Pulse_Output</Name>)',
    r'\g<1>1210.0\2',
    new_content
)
new_content = re.sub(
    r'(<Name>Timer_Sim_Pulse_Output</Name>\s*</AttributeList>.*?<LogicalAddress>%M)210\.0(</LogicalAddress>)',
    r'\g<1>1210.0\2',
    new_content,
    flags=re.DOTALL
)

# Replace address for Sim_Dir
new_content = re.sub(
    r'(<LogicalAddress>%M)210\.1(</LogicalAddress>\s*<Name>Sim_Dir</Name>)',
    r'\g<1>1210.1\2',
    new_content
)
new_content = re.sub(
    r'(<Name>Sim_Dir</Name>\s*</AttributeList>.*?<LogicalAddress>%M)210\.1(</LogicalAddress>)',
    r'\g<1>1210.1\2',
    new_content,
    flags=re.DOTALL
)

# Let's check if the addresses were changed
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("PLC Tag addresses updated successfully!")
