"""Fix source placeholder detection and deduplication in nodes.py."""
import re

with open("src/nodes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find and update the placeholder_phrases list
for i, line in enumerate(lines):
    if '"source not provided"' in line:
        # Found the placeholder list area - update it
        lines[i] = line  # keep "source not provided"
        # Add "document not explicitly cited" after "no source"
        for j in range(i+1, min(i+10, len(lines))):
            if '"no source",' in lines[j]:
                lines[j] = lines[j].rstrip() + '\n'
                # Insert new placeholder phrases after "no source"
                new_phrases = [
                    '                "document not explicitly cited",\n',
                ]
                # Insert after the current line
                for k, np in enumerate(new_phrases):
                    lines.insert(j+1+k, np)
                break
        break

# Now find and update the source validation to catch "Source 1" patterns
for i, line in enumerate(lines):
    if 'is_placeholder and rest' in line and 'valid_sources' in line:
        # Add the "Source N" pattern check before this line
        indent = '                    '
        new_lines = [
            f'{indent}# Also check for generic placeholder patterns like "Source 1"\n',
            f'{indent}if not is_placeholder and re.match(r"^source\\s+\\d+$", rest.lower()):\n',
            f'{indent}    is_placeholder = True\n',
            f'{indent}# Check for "[n] Document not explicitly cited" pattern\n',
            f'{indent}if not is_placeholder and "not explicitly cited" in rest.lower():\n',
            f'{indent}    is_placeholder = True\n',
        ]
        for j, nl in enumerate(new_lines):
            lines.insert(i+j, nl)
        break

with open("src/nodes.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Source validation updated successfully")
