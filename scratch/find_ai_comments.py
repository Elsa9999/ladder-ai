import os
import re

def find_ai_comments():
    xml_files = []
    # Scan the entire workspace
    for root, dirs, files in os.walk(r'd:\AI_Agent_PLC_LADDER_ONLY'):
        # Skip git and agent system files
        if '.git' in root or '.system_generated' in root or '.gemini' in root or 'antigravity' in root:
            continue
        for file in files:
            if file.endswith(('.xml', '.py', '.cs', '.md', '.txt')):
                xml_files.append(os.path.join(root, file))

    print(f"Found {len(xml_files)} files. Scanning for standalone 'AI' or 'ai'...")
    
    # Regex to find word "AI" (case-insensitive) as a whole word
    pattern = re.compile(r'\b[aA][iI]\b')
    
    matches_count = 0
    for file_path in xml_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all matches with their surrounding context (lines)
            lines = content.splitlines()
            file_printed = False
            for line_idx, line in enumerate(lines, 1):
                if pattern.search(line):
                    # Double check it is not part of a tag name or attribute containing AI_
                    # E.g. <Name>AI_B3_Sequence_Count</Name> or Tag="AI_B3_Sequence_Count"
                    # The \b[aA][iI]\b regex already handles AI_ since '_' is a word character, 
                    # but let's print and inspect.
                    if not file_printed:
                        print(f"\nFile: {file_path}")
                        file_printed = True
                    print(f"  Line {line_idx}: {line.strip()}")
                    matches_count += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    print(f"\nTotal matches found: {matches_count}")

if __name__ == '__main__':
    find_ai_comments()
