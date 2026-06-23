import json

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines[-20:]:
        try:
            data = json.loads(line)
            print(f"[{data.get('step_index')}] {data.get('source')} | {data.get('type')}")
            content = data.get("content", "")
            if content:
                print("  " + content[:300].replace("\n", " "))
        except Exception as e:
            print("Error parsing line:", e)
