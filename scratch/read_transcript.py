import json
import sys

# Force stdout to be utf-8
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\lienb\.gemini\antigravity-ide\brain\0123c9f4-e5bc-424b-80d8-b015956965a4\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Find last 10 USER messages and the corresponding responses
user_steps = []
for i, line in enumerate(lines):
    try:
        data = json.loads(line)
        src = data.get("source")
        tp = data.get("type")
        if src == "USER_EXPLICIT" or tp == "USER_INPUT":
            user_steps.append((i, data))
    except Exception:
        pass

print(f"Found {len(user_steps)} user messages")
for idx, (line_no, step) in enumerate(user_steps[-10:]):
    print(f"\n=== User Message #{len(user_steps) - 10 + idx + 1} (Line {line_no}, Step {step.get('step_index')}) ===")
    print(step.get("content"))
    
    # Print next few steps up to the next user message to see the model's reply
    next_user_idx = len(lines)
    if idx + 1 < len(user_steps[-10:]):
        next_user_idx = user_steps[-10:][idx + 1][0]
    
    for j in range(line_no + 1, next_user_idx):
        try:
            d = json.loads(lines[j])
            if d.get("source") == "MODEL" and d.get("type") in ["PLANNER_RESPONSE", "FINAL_RESPONSE"]:
                content = d.get("content")
                if content:
                    print(f"--- Model Reply (Step {d.get('step_index')}) ---")
                    print(content)
        except Exception:
            pass

