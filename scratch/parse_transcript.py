import json

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            idx = data.get("step_index")
            if idx is not None:
                src = data.get("source")
                tp = data.get("type")
                content = data.get("content", "")
                if "media__1781198715584" in content or "media__1781198715584" in str(data):
                    print(f"[{idx}] {src} | {tp}")
                    print(content)
                    t_calls = data.get("tool_calls", [])
                    if t_calls:
                        for tc in t_calls:
                            print(f"    Tool: {tc.get('name')} -> {str(tc.get('args'))}")
        except Exception as e:
            pass
