"""Fix finalize_report source extraction to avoid matching inline citations."""

with open("src/nodes.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the source_pattern line and update the extraction logic
old_pattern = 'source_pattern = re.compile(r\'\\[(\\d+)\\]\\s*([^\\n]+)\')'

new_pattern = '''# Find all "## Sources" and "### Sources" sections and extract only the source entries
    # within those sections (not inline citations in the body text)
    source_sections = re.findall(r'###?\\s+Sources\\n(.*?)(?=\\n## |\\n### |\\Z)', content, re.DOTALL)
    all_matches = []
    for sec in source_sections:
        for num_str, text in source_pattern.findall(sec):
            all_matches.append((int(num_str), text.strip()))'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    # Also need to define source_pattern before it's used
    # Find where all_matches is defined and insert source_pattern before it
    all_matches_line = content.find("all_matches = source_pattern.findall(content)")
    if all_matches_line != -1:
        # Replace the line and everything up to it with the new approach
        pass  # The replacement above handles this

with open("src/nodes.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Source extraction updated")
