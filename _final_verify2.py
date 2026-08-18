import re

with open("report.md", "r", encoding="utf-8") as f:
    content = f.read()

# Get the markdown code block content (actual report)
md_start = content.find("```markdown")
md_end = content.rfind("```")
report_content = content[md_start:md_end]

# Count 85% mentions
count_85 = report_content.count("85%")
print(f"Issue 1: '85%' mentions in report body: {count_85}")
for i, line in enumerate(report_content.split("\n")):
    if "85%" in line:
        print(f"  Line {i+1}: ...{line.strip()[:150]}...")

# Count 'administrative task' mentions
count_admin = report_content.lower().count("administrative task")
print(f"\nIssue 1: 'administrative task' mentions: {count_admin}")

# Check for 'drug discovery' duplication
count_drug = report_content.lower().count("drug discovery")
print(f"\nIssue 1: 'drug discovery' mentions: {count_drug}")

# Issue 2: Broken citations
print("\n=== Issue 2: Broken citations ===")
sources_start = report_content.find("## Sources")
# Find all source entries
source_pattern = re.findall(r'\[(\d+)\]\s+(.+)', report_content[sources_start:])
print(f"Sources found in final Sources section:")
for num, text in source_pattern:
    print(f"  [{num}] {text.strip()[:80]}...")

# Check for placeholder sources
placeholder_count = 0
for num, text in source_pattern:
    text_lower = text.lower()
    if any(p in text_lower for p in ["source not provided", "not provided", "source #", "source 1"]):
        print(f"  PLACEHOLDER: [{num}] {text[:60]}")
        placeholder_count += 1
print(f"Placeholder sources: {placeholder_count}")

# Count all unique source numbers referenced in body
body_before_sources = report_content[:sources_start]
body_citations = set(re.findall(r'\[(\d+)\]', body_before_sources))
print(f"\nInline citation numbers in body: {sorted(body_citations, key=int)}")

source_nums = set(int(x) for x in re.findall(r'\[(\d+)\]', report_content[sources_start:]))
print(f"Source list numbers: {sorted(source_nums)}")

# Check orphaned citations
orphaned = body_citations - source_nums
print(f"Orphaned citations (in body but not in sources): {orphaned if orphaned else 'None'}")

# Issue 3: Capitalization typos
print("\n=== Issue 3: Capitalization typos ===")
typos = report_content.count("AGentic")
print(f"AGentic typos: {typos}")

# Standalone citation markers
standalone = re.findall(r'^\[\d+\]\s+\[\d+\]', report_content, re.MULTILINE)
print(f"\nStandalone citation lists at line start: {len(standalone)}")
