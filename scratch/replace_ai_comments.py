import os
import re

def clean_content(content):
    # We want to replace standalone word "AI", "Ai", "ai" (not followed by '_' or other word characters)
    # when it refers to AI/Agent.
    # Common patterns:
    # "AI mô phỏng" -> "Mô phỏng"
    # "AI mô phỏng cảm biến" -> "Mô phỏng cảm biến"
    # "Xung AI" -> "Xung mô phỏng"
    # "AI Agent" -> "Agent"
    # "AI_AGENT" -> "AGENT"
    # "AI" -> "" (or "mô phỏng" depending on context)
    
    # We can do specific phrase replacements first to make it natural:
    phrases = [
        (r'\b[aA][iI]\s+[mM]ô\s+phỏng\b', 'Mô phỏng'),
        (r'\b[aA][iI]\s+([aA]gent|[aA]gents)\b', r'\1'),
        (r'\b[xX]ung\s+[aA][iI]\b', 'Xung mô phỏng'),
        # Standalone AI, Ai, ai (case sensitive for uppercase/title case)
        # Avoid replacing vietnamese word "ai" if it's not related, but usually in comments it is.
        (r'\bAI\b', 'Mô phỏng'),
        (r'\bAi\b', 'Mô phỏng')
    ]
    
    modified = content
    changes = []
    
    for pattern_str, replacement in phrases:
        pattern = re.compile(pattern_str)
        # Find matches for logging
        for match in pattern.finditer(modified):
            changes.append((match.group(0), replacement))
        modified = pattern.sub(replacement, modified)
        
    return modified, changes

def main():
    target_dirs = [
        r'd:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC',
        r'd:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\HMI',
        r'd:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens'
    ]
    
    xml_files = []
    for root_dir in target_dirs:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
                    
    print(f"Found {len(xml_files)} XML files to process:")
    for f in xml_files:
        print(f" - {f}")
        
    total_changes = 0
    for file_path in xml_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content, changes = clean_content(content)
            
            if changes:
                print(f"\nModifying {file_path}:")
                for original, rep in set(changes):
                    print(f"  Replace '{original}' -> '{rep}'")
                total_changes += len(changes)
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                print(f"No changes in {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"\nDone. Total replacements made: {total_changes}")

if __name__ == '__main__':
    main()
