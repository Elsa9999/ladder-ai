with open("projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py", 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\r\n', '\n')

print("Index of Step 0 Params label:", content.find("# Step 0 Params"))
idx = content.find("main.add_network(\"Modbus TCP Client - Step 0 Mode\"")
print("Index of Step 0 Mode network:", idx)
if idx != -1:
    print("Exact snippet from file around that index:")
    print(repr(content[idx:idx+200]))
