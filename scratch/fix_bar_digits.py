import re

path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We only want to replace IntegerDigits inside Hmi.Screen.Bar blocks
def replace_in_bar(match):
    block = match.group(0)
    # Replace <IntegerDigits>3</IntegerDigits> with <IntegerDigits>2</IntegerDigits>
    new_block = re.sub(r'<IntegerDigits>3</IntegerDigits>', '<IntegerDigits>2</IntegerDigits>', block)
    return new_block

pattern = re.compile(r'<Hmi\.Screen\.Bar\b.*?>(.*?)</Hmi\.Screen\.Bar>', re.DOTALL | re.IGNORECASE)
new_content = pattern.sub(replace_in_bar, content)

# Check if changed
diff_count = len(re.findall(r'<IntegerDigits>3</IntegerDigits>', content)) - len(re.findall(r'<IntegerDigits>3</IntegerDigits>', new_content))
print(f"Replaced {diff_count} instances of IntegerDigits inside Hmi.Screen.Bar.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
