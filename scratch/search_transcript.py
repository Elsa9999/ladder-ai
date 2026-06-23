import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

filepath = r"C:\Users\lienb\.gemini\antigravity-ide\brain\ac2f8bbd-79e2-44eb-8d52-8f6f976c041d\.system_generated\logs\transcript.jsonl"

if not os.path.exists(filepath):
    print("Transcript not found at:", filepath)
    sys.exit(0)

with open(filepath, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        try:
            obj = json.loads(line)
            content = obj.get("content", "")
            tool_calls = obj.get("tool_calls", [])
            
            # Search in content or tool calls
            has_match = False
            if "update_tia" in str(content).lower() or "update_tia" in str(tool_calls).lower():
                has_match = True
            
            if has_match:
                print(f"--- Step {obj.get('step_index', idx)} (type: {obj.get('type')}) ---")
                if content:
                    print("Content:", content[:200] + "..." if len(str(content)) > 200 else content)
                if tool_calls:
                    print("Tool Calls:", json.dumps(tool_calls, indent=2))
        except Exception as e:
            pass
