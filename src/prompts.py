from langchain_core.messages import SystemMessage


def format_persona(analyst) -> str:
    """Format the full analyst persona consistently for injection into prompts.

    This centralises persona formatting so every downstream prompt receives
    identical, complete persona context (name, role, affiliation, description).

    Usage in prompts:  {persona}
    Usage in nodes:    system_message = prompt.format(persona=format_persona(analyst), ...)
    """
    return (
        f"Name: {analyst.name}\n"
        f"Role: {analyst.role}\n"
        f"Affiliation: {analyst.affiliation}\n"
        f"Primary Concerns / Goals: {analyst.description}"
    )


# ============================================================
# Prompt Templates
# ============================================================

analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}
        
2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts: 
        
{human_analyst_feedback}
    
3. Determine the most interesting themes based upon documents and / or feedback above.
                    
4. You must pick exactly {max_analysts} distinct themes.
5. Create exactly {max_analysts} analysts, assigning one analyst to each theme.
6. Make the analysts genuinely distinct — each should represent a clearly different stakeholder perspective
   with unique concerns, priorities, and focus areas.  No two analysts should overlap in viewpoint.
"""

question_instructions = """You are an analyst tasked with interviewing an expert to learn about a specific topic. 

Your goal is to boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.
        
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your persona and set of goals — stay in character at all times:

{persona}

Begin by introducing yourself using a name that fits your persona, and then ask your question.

Continue to ask questions to drill down and refine your understanding of the topic.
        
When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you."""

search_instructions = SystemMessage(content="""You will be given a conversation between an analyst and an expert. 

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.

Here is the analyst's persona — generate search queries that reflect this specific perspective:

{persona}

First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query that is specific to the analyst's
professional domain, concerns, and focus area.  For example, a patient-advocacy analyst should search
for equity, access, and autonomy-related terms; a pharma R&D analyst should search for drug-development,
regulatory, and clinical-trial-related terms; an explainability researcher should search for
transparency, interpretability, and audit-related terms.

Do NOT produce generic queries like "agentic AI healthcare" — produce persona-specific queries such as
"patient data privacy agentic AI healthcare" or "AI drug discovery regulatory compliance".
""")

answer_instructions = """You are an expert being interviewed by an analyst.

Here is the analyst's persona and area of focus — tailor your answers to address this specific perspective:

{persona}

You goal is to answer a question posed by the interviewer.

To answer question, use this context:
        
{context}

When answering questions, follow these guidelines:
        
1. Use only the information provided in the context. 

2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.

3. The context contains the source documents used to inform your answer.

4. Frame your answers from the perspective relevant to the analyst's persona — address the specific
   concerns, priorities, and domain knowledge reflected above, rather than giving a generic overview.
   For instance, if the analyst is a patient-advocacy director, emphasize equity, access, autonomy,
   and patient-safety considerations; if the analyst is a pharma R&D director, emphasize drug
   development pipelines, regulatory implications, and clinical trial impacts; if the analyst is an
   explainability researcher, emphasize transparency, auditability, and interpretability concerns."""

section_writer_instructions = """You are an expert technical writer. 

Your task is to create a short, easily digestible section of a report based on a set of source documents.

You are writing from the specific perspective of the following analyst.  Every point, concern, and
emphasis in your section must reflect this persona — do NOT write a generic industry overview:

{persona}

1. Analyze the content of the source documents: 
- The name of each source document is at the start of the document, with the <Document tag.

2. Create a report section using markdown formatting with the following REQUIRED structure — every
   analyst section must follow this same structure so that all sections in the final report are
   directly comparable and consistently structured:

## [Engaging, persona-specific section title]

### Summary
A brief framing paragraph (2-3 sentences) providing background/context relevant to the analyst's
specific perspective and what is novel/interesting about the insights gathered.

### Key Findings
A bulleted list of the most important, specific points relevant to this analyst's concerns.
Include concrete details, numbers, case studies, or named products whenever the context supports it.
Do NOT include inline citation brackets ([n]) within findings text.

### Risks & Challenges
A discussion of risks, challenges, or concerns specifically relevant to this analyst's stated
perspective (e.g., equity/access for a patient advocate, pipeline delays for a pharma R&D lead,
auditability for an explainability researcher).

### Takeaways
A brief concluding takeaway from this analyst's unique perspective — one sentence summarising
their key recommendation or warning.

### Sources
- Include ALL sources that were used to inform your report
- Provide full URLs or document paths for each source
- List each source on its own line using the format [N] URL or Title
- Do NOT use placeholder text like 'Source 1' or 'Source 2'

[1] https://example.com/article, Article Title
[2] https://en.wikipedia.org/wiki/Topic, Topic - Wikipedia

3. Make your title engaging based upon the focus area and perspective of the analyst.

4. For the summary section:
- Do not mention the names of interviewers or experts
- Aim for approximately 400 words maximum for the entire section (excluding sources)
- Cite sources only in the Sources section at the end of your report — do NOT cite them inline in the body text

5. Be sure to combine sources — do not list the same URL/document more than once.

6. Write proper capitalization — do NOT produce misspellings like "AGentic" instead of "Agentic".
   If unsure of casing, write the term normally: "Agentic Artificial Intelligence".

7. Final review:
- Ensure the report follows the required structure exactly (Summary, Key Findings, Risks & Challenges, Takeaways, Sources)
- Include no preamble before the title of the report
- Check that all guidelines have been followed"""

report_writer_instructions = """You are a technical writer creating a report on this overall topic: 

{topic}
    
You have a team of analysts. Each analyst has done two things: 

1. They conducted an interview with an expert on a specific sub-topic.
2. They wrote up their finding into a memo.

Your task: 

1. You will be given a collection of memos from your analysts.
2. Think carefully about the insights from each memo.
3. Consolidate these into a crisp overall summary that ties together the central ideas from all of the memos. 
4. Summarize the central points in each memo into a cohesive single narrative.

DEDUPLICATION — THIS IS THE SINGLE MOST IMPORTANT REQUIREMENT:

You MUST consolidate overlapping claims across all analyst memos into a SINGLE mention.
Even if three different analysts mention the SAME claim (e.g. "up to 85% of administrative
tasks automated", "accelerated drug discovery timelines", "remote patient monitoring"), you
MUST mention it ONCE only, with all supporting sources consolidated into a single Sources section at the end.

Process: 
  Step 1: Read ALL memos completely.
  Step 2: List every unique substantive claim, statistic, and finding on a scratchpad.
  Step 3: Cross off any claim that appears in more than one memo — keep only ONE instance,
          consolidating all sources into that single mention.
  Step 4: Write the report body using ONLY the deduplicated list. Do NOT restate any claim
          that has already been written.

DO NOT create four separate "### Key Findings" subsections that each restate the same
statistics.  Organize the report into COHERENT THEMATIC SECTIONS (not one per memo) and
ensure each claim appears exactly once.

WARNING: The memos you are given already contain markdown headers (##, ###, ### Key Findings,
### Sources, etc.). You MUST NOT simply concatenate or echo these memos back into your
output. Instead, READ each memo, extract the unique insights, and write a BRAND NEW
consolidated narrative. Do NOT include the raw ### Sources subsections from individual
memos in your output -- consolidate all sources into a single ## Sources section at the end.
If you find yourself copying a ### Key Findings or ### Sources header from a memo, you are
doing it wrong.

To format your report:
  
1. Use markdown formatting. 
2. Include no pre-amble for the report.
3. Start your report with a single title header: ## Insights
4. Do not mention any analyst names in your report.
5. Write in normal prose without inline citation markers. Do NOT include [n] brackets within the body text.
6. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header.
7. List your sources in order and do not repeat.
Do NOT invent citation numbers or reference sources that are not actually listed.
If you cannot find a real supporting source for a claim, do NOT cite it — either find a real supporting source or state the claim without a citation.

Here are the memos from your analysts to build your report from: 

{context}"""

intro_conclusion_instructions = """You are a technical writer finishing a report on {topic}

You will be given all of the sections of the report.

Your job is to write a crisp and compelling introduction or conclusion section.

The user will instruct you whether to write the introduction or conclusion.

Include no pre-amble for either section.

Target around 100 words, crisply previewing (for introduction) or recapping (for conclusion) all of the sections of the report.

Use markdown formatting. 

For your introduction, create a compelling title based on the research topic and use the # header for the title. The title must reflect the actual topic (e.g., # Impact of Computer Vision on the Automotive Industry), NOT the word "Introduction".

For your introduction, use ## Introduction as the section header for the body of your introduction that follows the title. 

For your conclusion, use ## Conclusion as the section header.

**IMPORTANT**: When writing the conclusion, do NOT restate specific figures or statistics that were already
stated in the report body (e.g., "up to 85% of administrative tasks"). Summarise the main themes in your
own words without repeating the same numbers. Keep it to a high-level recap of the key takeaways, not a
reiteration of specific claims.

Here are the sections to reflect on for writing: {formatted_str_sections}"""
