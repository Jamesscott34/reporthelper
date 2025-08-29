"""
Breakdown Prompts for AI Document Processing

This module contains specialized prompts for different types of document breakdowns.
"""

# Base prompts for different document types
BREAKDOWN_PROMPTS = {
    "general": [
        {
            "name": "structured_breakdown",
            "prompt": """You are a content breakdown assistant. Your task is to take a full document and break it down clearly step-by-step.

Use numbered or bullet point format. Avoid AI tone. Keep it clear, short, and professional.

Example output format:
1. Introduction: Describes the project background
2. Methodology: Outlines data collection
3. Results: Summarizes findings
4. Conclusion: Provides final recommendations

Now, analyze the following text and create a structured breakdown:

{text}

Please provide a clear, structured breakdown with numbered sections:""",
        },
        {
            "name": "detailed_analysis",
            "prompt": """Analyze this document and create a comprehensive step-by-step breakdown.

Requirements:
- Use clear, numbered sections
- Include main topics and subtopics
- Highlight key points and findings
- Maintain professional tone
- Focus on actionable insights

Document content:
{text}

Create a detailed breakdown:""",
        },
        {
            "name": "executive_summary",
            "prompt": """Create an executive summary breakdown of this document.

Format:
1. Overview: Main purpose and scope
2. Key Points: Important findings and insights
3. Methodology: How the work was conducted
4. Results: Main outcomes and conclusions
5. Recommendations: Suggested next steps

Document:
{text}

Provide an executive summary breakdown:""",
        },
    ],
    "step_by_step": [
        {
            "name": "detailed_steps_links_commands",
            "prompt": """You are an expert technical writing assistant. Transform the provided text into a clear, beginner-friendly, step-by-step guide that greatly expands the original.

Primary goal
- Turn complex content into a comprehensive how-to with numbered steps and practical actions anyone can follow.

What to include (mandatory)
1) Overview: plain-language summary and expected outcomes.
2) Preparation checklist: required tools/software with OFFICIAL links only; OS support (Windows/macOS/Linux); prerequisites.
3) Step-by-step instructions (core): for each step include What to do, Why it matters, exact commands and/or GUI clicks.
   - Windows (PowerShell): use fenced blocks marked powershell
   - Linux/macOS (bash): use fenced blocks marked bash
   - Config snippets with proper language labels (e.g., nginx, yaml, json)
   - Verification checks and common troubleshooting tips per step
   - If OS differs, show per-OS subsections
4) Examples/analogies for abstract ideas.
5) Visual aids suggestions (e.g., simple diagram descriptions).
6) Sources: official links only; do NOT invent links. If unknown, say so.

Constraints and style
- Keep a logical flow; short sentences; no fluff.
- Prefer secure defaults; do not invent versions or links.
- Include a brief "Summary & Next Steps" at the end.
- Auto-example rule: If the input asks to "choose one", "give an example", or does not specify a concrete case, select a sensible, specific example and apply the full guide to that example. If the domain implies security/OWASP and no example is given, use Cross-Site Scripting (XSS) as the default. Do not ask follow-up questions—state any assumptions briefly and proceed.
- Auto-report rule: If the input requests a "report" or similar deliverable, generate a full report instead of a step-by-step guide. Minimum length: 500 words (meet any explicit word count if provided). Include clear numbered sections, concise prose, and image placeholders with descriptive captions (e.g., "Figure 1.1: Data Flow Diagram").
- Output policy: Do not repeat these instructions or the input verbatim. Produce the final deliverable only.

SECTION: {section}

CONTENT:
{text}
""",
        }
    ],
    "academic": [
        {
            "name": "research_paper",
            "prompt": """Break down this academic research paper into clear sections.

Expected structure:
1. Abstract: Main research question and findings
2. Introduction: Background and objectives
3. Literature Review: Previous research
4. Methodology: Research design and methods
5. Results: Key findings and data
6. Discussion: Interpretation of results
7. Conclusion: Implications and future work

Research paper content:
{text}

Create an academic breakdown:""",
        },
        {
            "name": "thesis_dissertation",
            "prompt": """Analyze this thesis or dissertation and create a comprehensive breakdown.

Structure:
1. Research Problem: Main question being addressed
2. Literature Review: Theoretical framework
3. Methodology: Research approach
4. Data Analysis: Key findings
5. Discussion: Interpretation and implications
6. Conclusions: Summary and recommendations

Thesis content:
{text}

Provide a thesis breakdown:""",
        },
    ],
    "business": [
        {
            "name": "business_report",
            "prompt": """Break down this business report into actionable sections.

Structure:
1. Executive Summary: Key findings and recommendations
2. Business Context: Market and competitive analysis
3. Financial Analysis: Key metrics and performance
4. Strategic Recommendations: Action items
5. Implementation Plan: Next steps and timeline

Business report content:
{text}

Create a business breakdown:""",
        },
        {
            "name": "project_proposal",
            "prompt": """Analyze this project proposal and create a structured breakdown.

Sections:
1. Project Overview: Purpose and objectives
2. Scope: What will be delivered
3. Timeline: Key milestones and deadlines
4. Resources: Required personnel and budget
5. Risks: Potential challenges and mitigation
6. Success Criteria: How success will be measured

Proposal content:
{text}

Provide a project breakdown:""",
        },
    ],
    "technical": [
        {
            "name": "technical_documentation",
            "prompt": """Break down this technical documentation into clear sections.

Structure:
1. Overview: Purpose and scope
2. System Architecture: Technical design
3. Implementation: Key components and processes
4. Configuration: Setup and deployment
5. Troubleshooting: Common issues and solutions
6. Maintenance: Ongoing support requirements

Technical content:
{text}

Create a technical breakdown:""",
        },
        {
            "name": "user_manual",
            "prompt": """Analyze this user manual and create a step-by-step breakdown.

Sections:
1. Getting Started: Initial setup and installation
2. Basic Operations: Core functionality
3. Advanced Features: Complex operations
4. Troubleshooting: Common problems and solutions
5. Reference: Quick reference guide

Manual content:
{text}

Provide a user manual breakdown:""",
        },
    ],
}

# Specialized prompts for specific content types
SPECIALIZED_PROMPTS = {
    "code_documentation": {
        "name": "code_analysis",
        "prompt": """Analyze this code documentation and create a technical breakdown.

Structure:
1. Overview: Purpose and functionality
2. Architecture: System design and components
3. API Reference: Key functions and methods
4. Examples: Usage examples and patterns
5. Best Practices: Coding standards and guidelines
6. Deployment: Installation and configuration

Code documentation:
{text}

Create a code documentation breakdown:""",
    },
    "legal_document": {
        "name": "legal_analysis",
        "prompt": """Break down this legal document into clear sections.

Structure:
1. Parties: Who is involved
2. Purpose: Main objective of the document
3. Terms: Key terms and conditions
4. Obligations: Responsibilities of each party
5. Timeline: Important dates and deadlines
6. Consequences: What happens if terms are violated

Legal document content:
{text}

Provide a legal document breakdown:""",
    },
    "medical_report": {
        "name": "medical_analysis",
        "prompt": """Analyze this medical report and create a structured breakdown.

Structure:
1. Patient Information: Demographics and history
2. Assessment: Medical evaluation and findings
3. Diagnosis: Medical conditions identified
4. Treatment Plan: Recommended interventions
5. Follow-up: Monitoring and next steps
6. Recommendations: Lifestyle and preventive measures

Medical report content:
{text}

Create a medical report breakdown:""",
    },
}


def get_prompts_for_content(text: str, content_type: str = "general") -> list:
    """
    Get appropriate prompts based on content type and text analysis.

    Args:
        text: Document text to analyze
        content_type: Type of content (general, academic, business, technical)

    Returns:
        List of prompts to try
    """
    prompts = []

    # Add base prompts for the content type
    if content_type in BREAKDOWN_PROMPTS:
        prompts.extend(BREAKDOWN_PROMPTS[content_type])

    # Add general prompts as fallback
    if content_type != "general":
        prompts.extend(BREAKDOWN_PROMPTS["general"])

    # Add specialized prompts based on content analysis
    if _contains_code(text):
        prompts.append(SPECIALIZED_PROMPTS["code_documentation"])

    if _contains_legal_terms(text):
        prompts.append(SPECIALIZED_PROMPTS["legal_document"])

    if _contains_medical_terms(text):
        prompts.append(SPECIALIZED_PROMPTS["medical_report"])

    return prompts


def _contains_code(text: str) -> bool:
    """Check if text contains code-like content."""
    code_indicators = [
        "def ",
        "class ",
        "function",
        "import ",
        "var ",
        "const ",
        "public ",
        "private ",
    ]
    return any(indicator in text.lower() for indicator in code_indicators)


def _contains_legal_terms(text: str) -> bool:
    """Check if text contains legal terminology."""
    legal_terms = [
        "whereas",
        "hereby",
        "party",
        "agreement",
        "contract",
        "terms",
        "conditions",
        "liability",
    ]
    return any(term in text.lower() for term in legal_terms)


def _contains_medical_terms(text: str) -> bool:
    """Check if text contains medical terminology."""
    medical_terms = [
        "diagnosis",
        "treatment",
        "patient",
        "symptoms",
        "medication",
        "prescription",
        "clinical",
    ]
    return any(term in text.lower() for term in medical_terms)
