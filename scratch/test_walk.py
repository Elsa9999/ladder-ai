import os
path = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC'
print("Files in directory:")
for f in os.listdir(path):
    print(f, f.endswith('.xml'))
