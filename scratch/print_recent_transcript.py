import json

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    print("Total lines in transcript:", len(lines))
    for i in range(max(0, len(lines)-15), len(lines)):
        try:
            data = json.loads(lines[i])
            idx = data.get("step_index")
            src = data.get("source")
            tp = data.get("type")
            print(f"[{idx}] {src} | {tp}")
            content = data.get("content", "")
            print(content[:500].strip())
            print("="*40)
        except Exception as e:
            print(f"Line {i+1} parse error:", e)
