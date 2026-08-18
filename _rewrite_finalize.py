"""Rewrite finalize_report in nodes.py."""

with open("src/nodes.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find and replace the entire finalize_report function
start_marker = "def finalize_report(state: ResearchGraphState):"
start_idx = content.find(start_marker)
if start_idx == -1:
    print("ERROR: Could not find finalize_report")
    exit(1)

end_marker = 'return {"final_report": final_report}'
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("ERROR: Could not find end of finalize_report")
    exit(1)
end_idx += len(end_marker)

new_func = r'''def finalize_report(state: ResearchGraphState):
    import re

    content = state["content"]
    if content.startswith("## Insights"):
        content = content[len("## Insights"):].lstrip()

    # Extract ALL sources from the content. There may be multiple "## Sources"
    # or "### Sources" sections from individual analyst sections that the
    # report writer included verbatim. We collect and deduplicate them all.
    source_pattern = re.compile(r'\[(\d+)\]\s*([^\n]+)')
    all_matches = source_pattern.findall(content)

    placeholder_phrases = [
        "source not provided", "source not found",
        "not provided in the given", "not found in", "no source",
        "document not explicitly cited", "source #", "source 1",
        "source 2", "<document", "document source",
    ]

    unique_sources = []
    seen_texts = set()
    for num_str, text in all_matches:
        text = text.strip()
        text_lower = text.lower()
        is_placeholder = any(p in text_lower for p in placeholder_phrases)
        if is_placeholder or not text:
            continue
        if text_lower in seen_texts:
            continue
        seen_texts.add(text_lower)
        unique_sources.append(text)

    # Strip source sections from body for clean citation handling
    body_parts = re.split(r'###?\s+Sources', content)
    body_content = body_parts[0]

    # Build mapping: old citation number -> new sequential number
    num_map = {}
    new_num = 1
    seen_texts2 = set()
    for num_str, text in all_matches:
        text = text.strip()
        text_lower = text.lower()
        is_placeholder = any(p in text_lower for p in placeholder_phrases)
        if is_placeholder or not text or text_lower in seen_texts2:
            continue
        seen_texts2.add(text_lower)
        num_map[int(num_str)] = new_num
        new_num += 1

    def remap_citation(match):
        old_num = int(match.group(1))
        if old_num in num_map:
            return f"[{num_map[old_num]}]"
        # Remove orphaned citation with surrounding parens if present
        return ""

    body_content = re.sub(r'\[(\d+)\]', remap_citation, body_content)
    # Clean up empty parens left by removed citations
    body_content = re.sub(r'\(\s*\)', '', body_content)
    body_content = re.sub(r'\s{3,}', '  ', body_content)

    # Fix common capitalization artifacts
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        body_content = re.sub(_typo, "Agentic", body_content)
    body_content = re.sub(r'agnetic-ai', 'agentic-ai', body_content)

    introduction = state["introduction"]
    introduction = re.sub(r"^(#+)\s*(#+\s*)?", "# ", introduction, count=1) if introduction.startswith("#") else introduction
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        introduction = re.sub(_typo, "Agentic", introduction)
        introduction = re.sub(r'agnetic-ai', 'agentic-ai', introduction)
    conclusion = state["conclusion"]
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        conclusion = re.sub(_typo, "Agentic", conclusion)
        conclusion = re.sub(r'agnetic-ai', 'agentic-ai', conclusion)

    formatted_sources = "\n\n".join(
        f"[{i+1}] {src}" for i, src in enumerate(unique_sources)
    )

    final_report = (
        introduction + "\n\n---\n\n" +
        body_content + "\n\n---\n\n" +
        conclusion
    )
    final_report += "\n\n## Sources\n" + formatted_sources

    return {"final_report": final_report}'''

content = content[:start_idx] + new_func + content[end_idx:]

with open("src/nodes.py", "w", encoding="utf-8") as f:
    f.write(content)

print("finalize_report completely rewritten successfully")
