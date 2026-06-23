import json
import os

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\ac2f8bbd-79e2-44eb-8d52-8f6f976c041d\.system_generated\logs\transcript.jsonl"

if not os.path.exists(log_path):
    print("Transcript path does not exist:", log_path)
else:
    print("Transcript path exists!")
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        print("Total lines in transcript:", len(lines))
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                content = str(data.get("content", ""))
                tool_calls = str(data.get("tool_calls", ""))
                # Search for keywords
                if "Button_10" in content or "Button_10" in tool_calls or "compilation aborted" in content or "aborted" in content:
                    print(f"Match found on step_index: {data.get('step_index')}, source: {data.get('source')}, type: {data.get('type')}")
                    # Print snippet
                    print("CONTENT SNIPPET:")
                    print(content[:1000])
                    print("="*60)
            except Exception as e:
                pass
