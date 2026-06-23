import json

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            idx = data.get("step_index")
            if idx is not None and 4350 <= idx < 4380:
                src = data.get("source")
                tp = data.get("type")
                content = data.get("content", "")
                print(f"[{idx}] {src} | {tp}")
                print(content[:1000].strip())
                print("="*40)
        except Exception as e:
            pass
