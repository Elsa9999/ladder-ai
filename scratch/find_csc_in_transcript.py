import json
import re

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

print("Searching for C# compilation or execution commands in log...")
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            tool_calls = data.get("tool_calls", [])
            for call in tool_calls:
                # check if call calls run_command or manage_task
                args = call.get("Arguments", {})
                if isinstance(args, dict):
                    cmd = args.get("CommandLine", "")
                    if cmd and (".cs" in cmd or "csc" in cmd or "compile" in cmd or "import_screen" in cmd):
                        print(f"Step {data.get('step_index')}: {cmd}")
        except Exception as e:
            pass
