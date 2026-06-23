import json

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "1781198715584" in line:
            try:
                data = json.loads(line)
                idx = data.get("step_index")
                src = data.get("source")
                tp = data.get("type")
                content = data.get("content", "")
                print(f"Line {i+1}: idx={idx}, source={src}, type={tp}")
                print("Content:")
                print(content[:1000])
                print("-" * 50)
            except Exception as e:
                print(f"Line {i+1} raw match: {line[:500]}")
