import sys
sys.path.append('Ladder')
sys.stdout.reconfigure(encoding='utf-8')
from Agent_LAD_Library import TIALadderBuilder
b = TIALadderBuilder('TestOB', '1', 'OB')
b.add_network('Test', [('MOVE', 'AI_Test_Var', 'AI_Dest_Var')])
xml = b.generate_xml()
# Find Component lines
for line in xml.splitlines():
    if 'Component' in line:
        print(line.strip())
