import re

with open("src/prompts.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find and replace the specific lines
old_line1 = "2. They write up their finding into a memo."
new_line1 = "2. They wrote up their finding into a memo."

old_line2 = "3. Use no sub-heading."
new_line2 = ""

old_line3 = "4. Start your report with a single title header: ## Insights"
new_line3 = "3. Start your report with a single title header: ## Insights"

old_line4 = "5. Do not mention any analyst names in your report."
new_line4 = "4. Do not mention any analyst names in your report."

old_line5 = "6. Preserve any citations in the memos, which will be annotated in brackets, for example [1] or [2]."
new_line5 = ("5. **CRITICAL**: When summarising claims from the memos, you MUST preserve inline "
              "citations.  If a claim in a memo states \"[1] The study found X,\" then your "
              "summary must include \"[1]\" next to that claim.  Do not strip citations during "
              "summarisation.  This ensures every claim in your report can be traced back to "
              "a specific source.")

old_line6 = "7. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header."
new_line6 = "6. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header."

old_line7 = "8. List your sources in order and do not repeat."
new_line7 = "7. List your sources in order and do not repeat."

replacements = [
    (old_line1, new_line1),
    (old_line2, new_line2),
    (old_line3, new_line3),
    (old_line4, new_line4),
    (old_line5, new_line5),
    (old_line6, new_line6),
    (old_line7, new_line7),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: '{old[:50]}...' -> '{new[:50]}...'")
    else:
        print(f"NOT FOUND: '{old[:50]}...'")

with open("src/prompts.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone - report_writer_instructions updated")
