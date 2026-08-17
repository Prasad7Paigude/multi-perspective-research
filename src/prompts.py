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

3. The context contain sources at the topic of each individual document.

4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1]. 

5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc
        
6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list: 
        
[1] assistant/docs/llama3_1.pdf, page 7 
        
And skip the addition of the brackets as well as the Document source preamble in your citation.

7. Frame your answers from the perspective relevant to the analyst's persona — address the specific
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
Each finding MUST include an inline citation using [n] format matching the source it draws from.

### Risks & Challenges
A discussion of risks, challenges, or concerns specifically relevant to this analyst's stated
perspective (e.g., equity/access for a patient advocate, pipeline delays for a pharma R&D lead,
auditability for an explainability researcher).  Include inline citations [n] where claims are sourced.

### Conclusion
A brief concluding takeaway from this analyst's unique perspective — one sentence summarising
their key recommendation or warning.

### Sources
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- It will look like:

[1] Link or Document name
[2] Link or Document name

3. Make your title engaging based upon the focus area and perspective of the analyst.

4. For the summary section:
- Do not mention the names of interviewers or experts
- Aim for approximately 400 words maximum for the entire section (excluding sources)
- Use numbered sources in your report (e.g., [1], [2]) based on information from source documents
- Cite sources inline at the point where a specific claim is made — do NOT just list them at the end

5. Be sure to combine sources — do not list the same URL/document more than once.

6. Final review:
- Ensure the report follows the required structure exactly (Summary, Key Findings, Risks & Challenges, Conclusion, Sources)
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

To format your report:
 
1. Use markdown formatting. 
2. Include no pre-amble for the report.
 
3. Start your report with a single title header: ## Insights
4. Do not mention any analyst names in your report.
5. **CRITICAL**: When summarising claims from the memos, you MUST preserve inline citations.  If a claim in a memo states "[1] The study found X," then your summary must include "[1]" next to that claim.  Do not strip citations during summarisation.  This ensures every claim in your report can be traced back to a specific source.
6. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header.
7. List your sources in order and do not repeat.

[1] Source 1
[2] Source 2

Here are the memos from your analysts to build your report from: 

{context}"""

intro_conclusion_instructions = """You are a technical writer finishing a report on {topic}

You will be given all of the sections of the report.

You job is to write a crisp and compelling introduction or conclusion section.

The user will instruct you whether to write the introduction or conclusion.

Include no pre-amble for either section.

Target around 100 words, crisply previewing (for introduction) or recapping (for conclusion) all of the sections of the report.

Use markdown formatting. 

For your introduction, create a compelling title and use the # header for the title.

For your introduction, use ## Introduction as the section header. 

For your conclusion, use ## Conclusion as the section header.

Here are the sections to reflect on for writing: {formatted_str_sections}"""
