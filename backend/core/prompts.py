"""
Prompt templates for Gemini API calls.
"""

# System context that guides all generation
SYSTEM_CONTEXT = """
You are an expert technical hiring manager with 10+ years of experience
creating take-home assignments. Your goal is to generate assignments that:

1. Reflect actual job responsibilities, not generic coding challenges
2. Respect candidate time with realistic scope
3. Provide clear evaluation criteria
4. Test for seniority-appropriate skills
5. Allow for creative interpretation and diverse solutions

Key principles:
- Be specific about business context (don't say "build a bookstore API")
- Break down time explicitly (setup, implementation, testing, docs)
- Define must-have vs nice-to-have clearly
- Create rubrics that prevent evaluator bias
- Flag when scope doesn't match time budget

CRITICAL - Requirements must be OUTCOME-FOCUSED, not implementation-specific:
- DO NOT specify exact field names, data types, or schema details
- DO NOT prescribe specific validation rules (e.g., "max 100 chars", "email format")
- DO NOT dictate exact status values, enum options, or state machines
- DO NOT specify exact HTTP status codes or error message formats
- INSTEAD describe WHAT the system should accomplish, not HOW to implement it
- Let candidates make their own design decisions about data modeling
- Focus on capabilities and behaviors, not technical specifications
- Allow room for candidates to demonstrate architectural thinking

Example of BAD requirement (too prescriptive):
"Implement endpoint accepting title (string, max 100 chars), description (string, max 500 chars), status (enum: open, in_progress, closed)"

Example of GOOD requirement (outcome-focused):
"Implement an endpoint to create new requests with appropriate metadata. Consider what information is essential for tracking and managing requests."
"""


def build_prompt(instruction: str) -> str:
    """
    Build a complete prompt with system context.

    Args:
        instruction: Specific instruction for the task

    Returns:
        Complete prompt with system context
    """
    return f"{SYSTEM_CONTEXT}\n\n{instruction}"


def get_context_extraction_prompt(job_description: str, tech_stack: list[str]) -> str:
    """
    Prompt for extracting context from job description.

    Args:
        job_description: Full job description text
        tech_stack: List of required technologies

    Returns:
        Formatted prompt
    """
    instruction = f"""
Analyze this job description and extract:
1. Primary technical responsibilities (3-5 items)
2. Business domain and product context
3. Technologies that will be used daily
4. Team collaboration patterns (if mentioned)

Job Description: {job_description}
Tech Stack: {tech_stack}

Return your analysis in JSON format with keys:
- responsibilities (array of strings)
- business_domain (string)
- daily_technologies (array of strings)
- collaboration_patterns (string or null)
"""
    return build_prompt(instruction)


def get_scope_definition_prompt(
    context: dict,
    seniority_level: str,
    time_budget_hours: float,
    must_evaluate: list[str],
    avoid_topics: list[str],
    company_context: str = None,
    current_challenges: str = None
) -> str:
    """
    Prompt for defining assignment scope.

    Args:
        context: Extracted job context
        seniority_level: Target seniority level
        time_budget_hours: Time budget in hours
        must_evaluate: Skills to evaluate
        avoid_topics: Topics to avoid
        company_context: Optional company context
        current_challenges: Optional team challenges

    Returns:
        Formatted prompt
    """
    must_have_time = time_budget_hours * 0.6
    nice_to_have_time = time_budget_hours * 0.2
    buffer_time = time_budget_hours * 0.2

    additional_context = ""
    if company_context:
        additional_context += f"\nCompany Context: {company_context}"
    if current_challenges:
        additional_context += f"\nCurrent Challenges: {current_challenges}"

    instruction = f"""
Create a take-home assignment for {seniority_level} level.
Time budget: {time_budget_hours} hours

Requirements:
1. Must-haves should take {must_have_time}h ({must_have_time * 60} minutes)
2. Nice-to-haves should take {nice_to_have_time}h ({nice_to_have_time * 60} minutes)
3. Include {buffer_time}h ({buffer_time * 60} minutes) buffer
4. Each requirement must tie to actual job responsibility
5. Include realistic business constraints (rate limits, data volumes, etc.)

Context: {context}
Focus areas: {must_evaluate}
Avoid: {avoid_topics}{additional_context}

IMPORTANT - Write requirements that are OUTCOME-FOCUSED, not prescriptive:
- Describe WHAT the system should do, not HOW to implement it
- DO NOT specify exact field names, data types, character limits, or enum values
- DO NOT dictate specific HTTP status codes or error formats
- Let candidates decide their own data models, validation rules, and API contracts
- Focus on capabilities ("track request status") not specifics ("status must be enum: open, closed")
- Allow creative interpretation so different candidates produce different valid solutions
- Requirements should test problem-solving and design skills, not ability to follow instructions

Return JSON with:
- title (string): Assignment title
- business_context (string): 200-400 words describing the business problem
- must_have_requirements (array): Each with description, estimated_time_minutes, why_it_matters
- nice_to_have_requirements (array): Same structure as must_have
- constraints (array of strings): High-level technical constraints (framework choices, no external DB, etc.) - NOT implementation details

Make the business context SPECIFIC and realistic, but keep requirements general enough for creative solutions.
"""
    return build_prompt(instruction)


def get_rubric_generation_prompt(
    scope: dict,
    seniority_level: str,
    must_evaluate: list[str]
) -> str:
    """
    Prompt for generating evaluation rubric.

    Args:
        scope: Assignment scope
        seniority_level: Target seniority level
        must_evaluate: Skills to evaluate

    Returns:
        Formatted prompt
    """
    instruction = f"""
Generate evaluation rubric for this take-home assignment:

Assignment: {scope.get('title')}
Seniority: {seniority_level}
Must evaluate: {must_evaluate}
Requirements: {scope.get('must_have_requirements')}

Create a rubric with 4-6 evaluation areas. For each area:
1. Define weight (sum must equal 1.0)
2. Junior expectation (if applicable)
3. Mid-level expectation
4. Senior expectation
5. Scoring guide (how to assign 1-5 score)

IMPORTANT - Evaluation should focus on:
- Quality of design DECISIONS, not adherence to a specific implementation
- How well the candidate justified their choices (in README or comments)
- Creativity and thoughtfulness in solving the problem
- Different valid approaches should score equally well
- DO NOT penalize candidates for choosing different field names, data structures, or API designs
- Evaluate the REASONING behind choices, not the specific choices themselves

Also provide:
- Common pitfalls candidates make (3-5 items) - focus on design/thinking mistakes, not implementation details
- Red flags that indicate poor understanding (3-5 items) - about fundamentals, not specific choices
- Green flags that indicate strong performance (3-5 items) - about design thinking and justification
- Calibration notes for consistent evaluation (2-3 paragraphs) - emphasize evaluating diverse solutions fairly

Return JSON with:
- scoring_rubric (array): Each item has area, weight, junior_expectation, mid_expectation, senior_expectation, scoring_guide
- common_pitfalls (array of strings)
- red_flags (array of strings)
- green_flags (array of strings)
- calibration_notes (string)

Ensure weights sum to exactly 1.0.
"""
    return build_prompt(instruction)


def get_time_breakdown_prompt(scope: dict, time_budget_hours: float) -> str:
    """
    Prompt for generating detailed time breakdown.

    Args:
        scope: Assignment scope
        time_budget_hours: Time budget in hours

    Returns:
        Formatted prompt
    """
    total_minutes = int(time_budget_hours * 60)

    instruction = f"""
Create a detailed time breakdown for this assignment:

Title: {scope.get('title')}
Must-have requirements: {scope.get('must_have_requirements')}
Nice-to-have requirements: {scope.get('nice_to_have_requirements')}
Total time budget: {time_budget_hours} hours ({total_minutes} minutes)

Break down the time into:
- setup_minutes: Environment setup, reading requirements
- core_implementation_minutes: Building the main functionality
- testing_minutes: Writing and running tests
- documentation_minutes: README, comments, etc.
- buffer_minutes: Unexpected issues, debugging

Return JSON with:
- total_minutes (integer): {total_minutes}
- setup_minutes (integer)
- core_implementation_minutes (integer)
- testing_minutes (integer)
- documentation_minutes (integer)
- buffer_minutes (integer)
- breakdown_valid (boolean): true if components sum to total_minutes +/- 5

Ensure all values are realistic and components sum correctly.
"""
    return build_prompt(instruction)


# JSON Schemas for structured output
CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "responsibilities": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5
        },
        "business_domain": {"type": "string"},
        "daily_technologies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "collaboration_patterns": {
            "type": ["string", "null"]
        }
    },
    "required": ["responsibilities", "business_domain", "daily_technologies"]
}

SCOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "business_context": {"type": "string"},
        "must_have_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "estimated_time_minutes": {"type": "integer"},
                    "why_it_matters": {"type": "string"}
                },
                "required": ["description", "estimated_time_minutes", "why_it_matters"]
            }
        },
        "nice_to_have_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "estimated_time_minutes": {"type": "integer"},
                    "why_it_matters": {"type": "string"}
                },
                "required": ["description", "estimated_time_minutes", "why_it_matters"]
            }
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["title", "business_context", "must_have_requirements", "nice_to_have_requirements", "constraints"]
}

RUBRIC_SCHEMA = {
    "type": "object",
    "properties": {
        "scoring_rubric": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {"type": "string"},
                    "weight": {"type": "number"},
                    "junior_expectation": {"type": "string"},
                    "mid_expectation": {"type": "string"},
                    "senior_expectation": {"type": "string"},
                    "scoring_guide": {"type": "string"}
                },
                "required": ["area", "weight", "junior_expectation", "mid_expectation", "senior_expectation", "scoring_guide"]
            }
        },
        "common_pitfalls": {
            "type": "array",
            "items": {"type": "string"}
        },
        "red_flags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "green_flags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "calibration_notes": {"type": "string"}
    },
    "required": ["scoring_rubric", "common_pitfalls", "red_flags", "green_flags", "calibration_notes"]
}

TIME_BREAKDOWN_SCHEMA = {
    "type": "object",
    "properties": {
        "total_minutes": {"type": "integer"},
        "setup_minutes": {"type": "integer"},
        "core_implementation_minutes": {"type": "integer"},
        "testing_minutes": {"type": "integer"},
        "documentation_minutes": {"type": "integer"},
        "buffer_minutes": {"type": "integer"},
        "breakdown_valid": {"type": "boolean"}
    },
    "required": ["total_minutes", "setup_minutes", "core_implementation_minutes", "testing_minutes", "documentation_minutes", "buffer_minutes", "breakdown_valid"]
}
