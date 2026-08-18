import re

with open("report.md", "r", encoding="utf-8") as f:
    content = f.read()

sources_idx = content.find("## Sources")
report_body = content[:sources_idx]

# Count citations in final report body
body_citations = re.findall(r'\[\d+\]', report_body)
unique_citations = sorted(set(body_citations), key=lambda x: int(x.strip('[]')))
print('=== FIX 6: Inline Citation Analysis ===')
print(f'Citations in final report body: {len(body_citations)} total, {len(unique_citations)} unique')
print(f'  {unique_citations}')

# Count citations in individual sections (in markdown code block preview)
section_start = content.find('### Interview Section (Preview)')
section_end = content.find('### Final Report')
section_preview = content[section_start:section_end]
section_citations = re.findall(r'\[\d+\]', section_preview)
print(f'Citations in interview section preview: {len(section_citations)}')
print()

# Check for repetitive phrases from original sample
print('=== FIX 3: Repetition Analysis ===')
print('Checking for phrases from original sample problem output:')
phrases = [
    'streamlining administrative tasks',
    'clinician burnout',
    'workforce shortages',
    'operational inefficiencies',
    'proactive patient monitoring',
]
for phrase in phrases:
    count = content.lower().count(phrase.lower())
    print(f'  "{phrase}": {count} occurrences')

print()
print('Checking for new near-duplicate repetitive phrases:')
repetitive_phrases = [
    'precision, responsiveness, and reliability',
    'up to 85%',
    'administrative tasks',
    'data security',
    'privacy concerns',
]
for phrase in repetitive_phrases:
    matches = list(re.finditer(re.escape(phrase), content, re.IGNORECASE))
    if len(matches) > 1:
        print(f'  "{phrase}": {len(matches)} occurrences (potential repetition)')
        for m in matches:
            start = max(0, m.start() - 20)
            end = min(len(content), m.end() + 20)
            context = content[start:end].replace('\n', ' ')
            print(f'    ...{context}...')
