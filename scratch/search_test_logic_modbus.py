import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/test_plc_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("PLC1 Modbus Simulator section:")
for i in range(13, 1034):
    line = lines[i]
    if 'mb_' in line.lower() or 'tcp' in line.lower() or 'holding' in line.lower() or 'buffer' in line.lower():
        print(f"Line {i+1}: {line.strip()}")

print("\nPLC2 Modbus Simulator section:")
for i in range(1035, len(lines)):
    line = lines[i]
    if 'mb_' in line.lower() or 'tcp' in line.lower() or 'holding' in line.lower() or 'buffer' in line.lower():
        print(f"Line {i+1}: {line.strip()}")
