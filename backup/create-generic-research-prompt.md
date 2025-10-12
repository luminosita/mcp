#This prompt generators generic research prompt in XML format and research artifact template in Markdown
#DO NOT USE IT FOR RESEARCH

## ROLE
You are a senior software product researcher with the strong technical background. Your expertise is in comparing published software products in the market, gather extensive information, capabilities, key features and finding important market and technical gaps to provide strong advises on a future product vision and roadmap.

## CONTEXT
We performed extensive deep research on three different software products:
    - Universal Secrets Management Tool 
    - MCP Server for AI-assisted software engineering
    - Product Management Backlog solution
All there researches produced very good results in the form of market analysis, identifing gaps, features/capabilities recommendation, and software architecture. The issue we found is that the results lack the common structure. Each research excelled in certain areas and left some important ones uncovered. True cause of the variations in the research outcome is the inconcistency and weak prompt formulation.

## GOAL
Establish a clear and comprehensive research prompt and research artifact template containing instructions to follow research structure, to cover all important areas, but at the same time provide enough freedom to a research AI agent to excel in finding new gaps and niches in the market and sophisticated synthesis of competitive products capabilities. Research artifact needs to be the main guide for product SDLC artifacts creation. 

## STEPS
- Do a deep analysis of the existing prompts and their corresponding research results
    - `backlog_prompt.md` -> `Backlog Solution Implementation Guidelines.md`
    - `mcp_prompt.md` -> `AI Agent MCP Server Implementation Report.md`
    - `shh_prompt.md` -> `Secrets Management Solution Research Report.md`
- Do a deep analysis of the existing generator prompt template (`generator-schema.xml`)
- Do a deep analysis of SDLC phases artifacts templates to clarify the requirements for each SDLC phase
- Synthesize sophisticated research artifact structure based on gathered information

## ANTI-HALLUCATIONS
- Clarify the goal and instructions by asking human to explain and confirm all the assumptions
- Proceed to generate output only after confirmation

## INSTRUCTIONS
- Research generator prompt is the AI Research Agent main input. Research artifact is the final output for an agent.
- Research Prompt must require human inputs on general product idea:
    - Problem overview
    - Target users (high-level)
    - Key capabilities (draft)
    - Initial constraints
    - Product references to include in the research
- Research Prompt must validate human input
- Research Prompt must contain anti-hallucation guardrails
- Research Prompt must clarify human inputs by asking questions
- Research Prompt can proceed with the research only after confirmation of clarity. Each LLM assumpation must be clarified and confirmed with human.
- Research Prompt must produce the research plan and wait for the confirmation
- Research Prompt must contain final research artifact validation checklist 
- Research Prompt must contain instructions to generate final research artifact with all research citations following `CITATION REQUIREMENTS`
- Research Prompt must follow `generator-schema.xml`. Add sections if required.
- Research Prompt must instruct formulation of overall architecture recommendation
- Research Prompt must instruct AI Research Agent to perform deep analysis of the existing products in the market and referenced products suggested by humans:
    - capabilities
    - key/string points
    - market gaps
    - technology gaps
- Research Prompt must instruct formulation of product capabilities and technology stack recommendations for the following areas, if applicable:
    - security
    - caching
    - observability
    - testing
    - backend repositories
    - frontend
    - API
    - CLI
    - Events and triggers
    - AI Agent assistance

- Research Artifact Template should provide abundant information and examples for SDLC phases artifacts requirements. Research Artifact Template is the main reference to establish sophisticated SDLC artifacts.
- Research Prompt must be formatted as XML
- Research Artifact Template must be formatted as Markdown

## VALIDATION CHECKLIST
- [ ] Research Prompt is in XML format
- [ ] Research Artifact Template is in Markdown format
- [ ] Reserch Prompt follows `generator-schema.xml`
- [ ] Research Prompt contains human input validation and clarification instructions
- [ ] Research Prompt contains anti-hallucation guardrails
- [ ] Research Prompt contains final research artifact validation checklist
- [ ] Research Prompt contains citation requirements
- [ ] Research Artifact Template contains clear XML structure
- [ ] Research Artifact Template structure is synthesized from referenced research documents
- [ ] Research Artifact Template structure correlates with SDLC phases artifacts requirements

## REFERENCES
- `docs/research/backlog/backlog_prompt.md`                                   #prompt used for backlog solution research
- `docs/research/backlog/Backlog Solution Implementation Guidelines.md`       #backlog solution research artifact 
- `docs/research/mcp/mcp_prompt.md`                                       #prompt used for mcp server research
- `docs/research/mcp/AI Agent MCP Server Implementation Report.md`        #mcp server research artifact 
- `docs/research/shh/shh_prompt.md`                                       #prompt used for secrets management research
- `docs/research/shh/Secrets Management Solution Research Report.md`      #secrets management research artifact 
- `prompts/templates/generator-schema.xml`                    #existing generator prompt template
- SDLC phases artifacts templates:
    - `prompts/templates/product-vision-template.xml`       #product vision template
    - `prompts/templates/epic-template.xml`                 #epic template
    - `prompts/templates/prd-template.xml`                  #prd template
    - `prompts/templates/backlog-story-template.xml`        #backlog user story template
    - `prompts/templates/adr-template.xml`                  #adr template
    - `prompts/templates/tech-spec-template.xml`            #tech spec template

## OUTPUT
- Save Research Generator Prompt to `prompts/research-generator.md`
- Save Research Artifact Template to `prompts/templates/research-artifact-template.md`

## CITATION REQUIREMENTS
```markdown
## **CRITICAL CITATION REQUIREMENTS FOR RESEARCH DOCUMENTS**

When creating research papers, technical documentation, or any content that references external sources, you MUST use standard Markdown footnote syntax throughout. This requirement ensures the document remains portable, academically rigorous, and verifiable across any Markdown renderer.

### **Inline Citation Format**

Whenever you reference information from a source, immediately follow the claim with a numbered footnote marker using this exact syntax: `[^1]`, `[^2]`, `[^3]`, etc. The number should increment sequentially throughout the entire document.

**Example of proper inline usage:**
"Anthropic's Contextual Retrieval demonstrated a 67% reduction in retrieval failures.[^1] This technique prepends 50-100 token context explanations to each chunk before embedding.[^1]"

**Critical rules for inline citations:**
- Place the footnote marker immediately after the period or punctuation, with no space between
- Use the same footnote number for multiple references to the same source
- Every factual claim, statistic, or technical detail that comes from research must have a citation
- Do not use parenthetical citations like (Source, 2024) - only use footnote markers

### **References Section Format**

At the very end of the document, after all content sections, create a section titled "## References" or "## Sources". Under this heading, list every footnote in numerical order using this exact format:

```markdown
[^1]: Author/Organization Name, "Article or Page Title", accessed [Month Day, Year], URL
[^2]: Author/Organization Name, "Article or Page Title", accessed [Month Day, Year], URL
```

**Example of properly formatted references:**
```markdown
## References

[^1]: Anthropic, "Introducing Contextual Retrieval", accessed September 2024, https://www.anthropic.com/news/contextual-retrieval
[^2]: Orkes, "Best Practices for Production-Scale RAG Systems — An Implementation Guide", accessed October 2024, https://orkes.io/blog/rag-best-practices/
[^3]: Voyage AI, "voyage-3-large: the new state-of-the-art general-purpose embedding model", accessed January 2025, https://blog.voyageai.com/2025/01/07/voyage-3-large/
```

**Critical rules for the references section:**
- Every footnote number used in the text must have a corresponding entry in this section
- Entries must be in numerical order without gaps
- Each entry must include: source name, article title in quotes, access date, and full URL
- URLs must be complete and clickable (include https://)
- If the exact access date is unknown, use the publication date or current date

### **What This Achieves**

This format ensures that when someone copies your document to any Markdown viewer (GitHub, Obsidian, Notion, static site generators, etc.), the footnotes will automatically create clickable superscript numbers in the text that link to the full reference at the bottom. The reader can click a number to jump to the source, then click back to return to their reading position.

### **Quality Checks Before Delivery**

Before delivering any research document, verify:
- Every factual claim has a footnote marker
- All footnote numbers in the text have matching entries in the References section
- No footnote numbers are skipped (1, 2, 3... not 1, 3, 5...)
- All URLs are complete and properly formatted
- The References section appears at the very end of the document

**Do not use alternative citation systems** like inline tags, parenthetical references, or embedded links for research citations. Only use the Markdown footnote syntax described above.
```
---
