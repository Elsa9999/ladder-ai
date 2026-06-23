import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\PLC_Tags_B3to7.xml"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        for i in range(50):
            line = f.readline()
            if not line:
                break
            print(line, end='')
else:
    print("File not found.")
