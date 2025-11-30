# Technical Product Specification: Take-Home Test Generator

## 1. Product Overview

### 1.1 Problem Statement
Engineering teams waste 468+ hours annually creating inconsistent take-home assignments. Candidates spend 3-4x stated time on poorly scoped tests. Current solutions generate generic challenges that don't reflect actual job requirements or company context.

### 1.2 Solution
AI-powered generator that creates realistic, scoped take-home assignments with business context, explicit time breakdowns, and standardized evaluation rubrics.

### 1.3 Success Metrics
- Assignment completion time matches stated estimate (±30 min, 80% of candidates)
- Evaluator scoring consistency (±10% variance between reviewers)
- Time-to-create reduced from 3 hours to 15 minutes
- Candidate completion rate >70% (vs industry average ~45%)

---

## 2. System Architecture

### 2.1 High-Level Components

```
┌─────────────────┐
│  Input Layer    │ → Job context, constraints, requirements
└────────┬────────┘
         ↓
┌─────────────────┐
│  Agent Core     │ → Analysis, scope validation, generation
└────────┬────────┘
         ↓
┌─────────────────┐
│  Output Layer   │ → Candidate brief, eval rubric, time breakdown
└─────────────────┘
```

### 2.2 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI for API endpoints
- Google Gemini Flash 2.5 for generation
- Pydantic for data validation

**Frontend (MVP):**
- React/TypeScript
- Form-based input interface
- Markdown renderer for output display

**Storage (Post-MVP):**
- PostgreSQL for assignment templates
- S3/local storage for generated artifacts

---

## 3. Data Models

### 3.1 Input Schema

```python
class AssignmentInput(BaseModel):
    # Required Fields
    job_title: str  # e.g., "Senior Backend Engineer"
    job_description: str  # Full JD text, 500-2000 chars
    tech_stack: List[str]  # e.g., ["Python", "FastAPI", "PostgreSQL"]
    time_budget_hours: float  # 2.0 to 8.0
    seniority_level: Literal["junior", "mid", "senior", "staff"]
    
    # Optional Fields
    company_context: Optional[str]  # Company description, product domain
    current_challenges: Optional[str]  # Team pain points, scaling issues
    must_evaluate: List[str]  # e.g., ["API design", "error handling"]
    avoid_topics: List[str]  # e.g., ["algorithms", "system design"]
    
    # Constraints
    candidate_can_use: Optional[List[str]]  # Allowed libraries/frameworks
    submission_format: Literal["github", "zip", "codesandbox"] = "github"
```

### 3.2 Output Schema

```python
class GeneratedAssignment(BaseModel):
    # Core Artifacts
    candidate_brief: CandidateBrief
    evaluator_guide: EvaluatorGuide
    time_breakdown: TimeBreakdown
    
    # Metadata
    assignment_id: str
    generated_at: datetime
    estimated_difficulty: Literal["easy", "medium", "hard"]
    scope_warnings: List[str]  # Flags if scope seems mismatched

class CandidateBrief(BaseModel):
    title: str
    business_context: str  # 200-400 words
    requirements: Requirements
    submission_guidelines: str
    evaluation_criteria: List[str]  # High-level areas
    time_estimate: str  # "3-4 hours"

class Requirements(BaseModel):
    must_have: List[Requirement]  # Core functionality
    nice_to_have: List[Requirement]  # Optional enhancements
    constraints: List[str]  # Rate limits, data volumes, etc.

class Requirement(BaseModel):
    description: str
    estimated_time_minutes: int
    why_it_matters: str  # Ties to actual job

class EvaluatorGuide(BaseModel):
    scoring_rubric: List[RubricItem]
    common_pitfalls: List[str]
    red_flags: List[str]
    green_flags: List[str]
    calibration_notes: str  # How to apply rubric consistently

class RubricItem(BaseModel):
    area: str  # e.g., "Error Handling"
    weight: float  # 0.0 to 1.0
    junior_expectation: str
    mid_expectation: str
    senior_expectation: str
    scoring_guide: str  # How to assign 1-5 score

class TimeBreakdown(BaseModel):
    total_minutes: int
    setup_minutes: int
    core_implementation_minutes: int
    testing_minutes: int
    documentation_minutes: int
    buffer_minutes: int
    breakdown_valid: bool  # Does math check out?
```

---

## 4. Core Agent Logic

### 4.1 Generation Pipeline

**Phase 1: Context Extraction (10-15 seconds)**
```python
def extract_context(input: AssignmentInput) -> JobContext:
    """
    Parse job description to identify:
    - Core technical responsibilities
    - Business domain (fintech, e-commerce, etc.)
    - Team structure clues
    - Implicit requirements
    """
    prompt = f"""
    Analyze this job description and extract:
    1. Primary technical responsibilities (3-5 items)
    2. Business domain and product context
    3. Technologies that will be used daily
    4. Team collaboration patterns (if mentioned)
    
    Job Description: {input.job_description}
    Tech Stack: {input.tech_stack}
    
    Return your analysis in JSON format with keys: responsibilities, 
    business_domain, daily_technologies, collaboration_patterns
    """
    return call_gemini(prompt, response_mime_type="application/json")
```

**Phase 2: Scope Definition (15-20 seconds)**
```python
def define_scope(context: JobContext, input: AssignmentInput) -> AssignmentScope:
    """
    Generate must-have vs nice-to-have requirements.
    Validate time budget is realistic.
    """
    must_have_time = input.time_budget_hours * 0.6
    nice_to_have_time = input.time_budget_hours * 0.2
    buffer_time = input.time_budget_hours * 0.2
    
    prompt = f"""
    Create a take-home assignment for {input.seniority_level} level.
    Time budget: {input.time_budget_hours} hours
    
    Requirements:
    1. Must-haves should take {must_have_time}h ({must_have_time * 60} minutes)
    2. Nice-to-haves should take {nice_to_have_time}h ({nice_to_have_time * 60} minutes)
    3. Include {buffer_time}h ({buffer_time * 60} minutes) buffer
    4. Each requirement must tie to actual job responsibility
    5. Include realistic business constraints (rate limits, data volumes, etc.)
    
    Context: {context.model_dump_json()}
    Focus areas: {input.must_evaluate}
    Avoid: {input.avoid_topics}
    
    Return JSON with: title, business_context, must_have_requirements, 
    nice_to_have_requirements, constraints
    
    Each requirement must have: description, estimated_time_minutes, why_it_matters
    """
    return call_gemini(prompt, response_mime_type="application/json")
```

**Phase 3: Validation (10 seconds)**
```python
def validate_scope(scope: AssignmentScope, input: AssignmentInput) -> ScopeValidation:
    """
    Self-critique: Does the assignment meet quality bars?
    """
    total_time = sum(r.estimated_time_minutes for r in scope.all_requirements)
    expected_time = input.time_budget_hours * 60
    
    checks = {
        'time_realistic': 0.85 <= (total_time / expected_time) <= 1.15,
        'has_business_context': len(scope.business_context) >= 200,
        'has_constraints': len(scope.constraints) >= 2,
        'requirements_count': 3 <= len(scope.must_have) <= 7,
        'seniority_appropriate': check_seniority_match(scope, input.seniority_level)
    }
    
    issues = [k for k, v in checks.items() if not v]
    
    return ScopeValidation(
        passed=all(checks.values()),
        issues=issues,
        warnings=generate_warnings(checks, scope, input)
    )
```

**Phase 4: Rubric Generation (15-20 seconds)**
```python
def generate_rubric(scope: AssignmentScope, input: AssignmentInput) -> EvaluatorGuide:
    """
    Create scoring guide with seniority-specific expectations.
    """
    prompt = f"""
    Generate evaluation rubric for this take-home assignment:
    
    Assignment: {scope.title}
    Seniority: {input.seniority_level}
    Must evaluate: {input.must_evaluate}
    Requirements: {scope.must_have}
    
    Create a rubric with 4-6 evaluation areas. For each area:
    1. Define weight (sum must equal 1.0)
    2. Junior expectation (if applicable)
    3. Mid-level expectation
    4. Senior expectation
    5. Scoring guide (how to assign 1-5 score)
    
    Also provide:
    - Common pitfalls candidates make
    - Red flags that indicate poor understanding
    - Green flags that indicate strong performance
    - Calibration notes for consistent evaluation
    
    Return JSON with: rubric_items, common_pitfalls, red_flags, 
    green_flags, calibration_notes
    """
    return call_gemini(prompt, response_mime_type="application/json")
```

### 4.2 Quality Gates

Each phase must pass validation:

```python
class QualityGate:
    def validate_context_extraction(self, context: JobContext) -> ValidationResult:
        """Context must include business domain and 3+ responsibilities"""
        issues = []
        
        if len(context.responsibilities) < 3:
            issues.append("Insufficient responsibilities extracted (min 3)")
        
        if not context.business_domain:
            issues.append("Business domain not identified")
        
        if not context.daily_technologies:
            issues.append("Daily technologies not specified")
        
        return ValidationResult(passed=len(issues) == 0, issues=issues)
    
    def validate_scope(self, scope: AssignmentScope, time_budget: float) -> ValidationResult:
        """Time estimates must sum to budget ±15%"""
        issues = []
        
        total_time = sum(r.estimated_time_minutes for r in scope.all_requirements)
        expected_minutes = time_budget * 60
        time_ratio = total_time / expected_minutes
        
        if not (0.85 <= time_ratio <= 1.15):
            issues.append(
                f"Time mismatch: requirements sum to {total_time}min "
                f"but budget is {expected_minutes}min (ratio: {time_ratio:.2f})"
            )
        
        if len(scope.business_context) < 200:
            issues.append("Business context too brief (min 200 chars)")
        
        if len(scope.must_have) < 3:
            issues.append("Too few must-have requirements (min 3)")
        
        return ValidationResult(passed=len(issues) == 0, issues=issues)
    
    def validate_rubric(self, rubric: List[RubricItem]) -> ValidationResult:
        """Rubric must cover evaluation areas and weights sum to 1.0"""
        issues = []
        
        weight_sum = sum(item.weight for item in rubric)
        if abs(weight_sum - 1.0) > 0.01:
            issues.append(f"Rubric weights sum to {weight_sum}, must be 1.0")
        
        if len(rubric) < 3:
            issues.append("Too few rubric items (min 3)")
        
        if len(rubric) > 7:
            issues.append("Too many rubric items (max 7, keep focused)")
        
        return ValidationResult(passed=len(issues) == 0, issues=issues)
```

---

## 5. API Endpoints

### 5.1 Core Endpoints

```
POST /api/v1/assignments/generate
Request: AssignmentInput
Response: GeneratedAssignment
Status: 201 Created | 400 Bad Request | 422 Validation Error
Time: ~60-90 seconds

POST /api/v1/assignments/validate
Request: AssignmentInput
Response: ValidationResult (without generating full assignment)
Status: 200 OK | 400 Bad Request
Time: ~15-20 seconds

GET /api/v1/assignments/{assignment_id}
Response: GeneratedAssignment
Status: 200 OK | 404 Not Found

POST /api/v1/assignments/{assignment_id}/refine
Request: RefinementFeedback
Response: GeneratedAssignment
Status: 200 OK | 404 Not Found
Time: ~45-60 seconds
```

### 5.2 Refinement Workflow

```python
class RefinementFeedback(BaseModel):
    assignment_id: str
    changes: List[Change]

class Change(BaseModel):
    type: Literal["adjust_time", "add_requirement", "remove_requirement", 
                  "change_focus", "adjust_difficulty"]
    description: str
    
# Example:
{
    "changes": [
        {"type": "adjust_time", "description": "Reduce to 3 hours"},
        {"type": "add_requirement", "description": "Add observability component"}
    ]
}
```

---

## 6. Gemini Integration

### 6.1 API Configuration

**Model Selection:**
- Use Gemini Flash 2.5 (gemini-2.5-flash-preview-05-21)
- Fast, cost-effective, supports JSON structured output
- Context window: 1M tokens (more than sufficient)

**Cost Analysis:**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Estimated tokens per request: 6,000-10,000 (input + output)
- Cost per assignment: ~$0.002-0.004 (significantly cheaper than Claude)

**Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 0.7,  # Balanced creativity and consistency
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
```

### 6.2 Client Implementation

```python
class GeminiClient:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-05-21",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    
    def generate_json(
        self, 
        prompt: str, 
        schema: Optional[dict] = None
    ) -> dict:
        """
        Generate structured JSON response from Gemini.
        
        Args:
            prompt: Instruction prompt
            schema: Optional JSON schema for validation
        
        Returns:
            Parsed JSON response
        """
        generation_config_with_json = {
            **generation_config,
            "response_mime_type": "application/json"
        }
        
        if schema:
            generation_config_with_json["response_schema"] = schema
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config_with_json
        )
        
        return json.loads(response.text)
    
    def generate_text(self, prompt: str) -> str:
        """Generate text response from Gemini."""
        response = self.model.generate_content(prompt)
        return response.text
```

### 6.3 Prompting Strategy

**System Context Pattern:**
```python
SYSTEM_CONTEXT = """
You are an expert technical hiring manager with 10+ years of experience 
creating take-home assignments. Your goal is to generate assignments that:

1. Reflect actual job responsibilities, not generic coding challenges
2. Respect candidate time with realistic scope
3. Provide clear evaluation criteria
4. Test for seniority-appropriate skills

Key principles:
- Be specific about business context (don't say "build a bookstore API")
- Break down time explicitly (setup, implementation, testing, docs)
- Define must-have vs nice-to-have clearly
- Create rubrics that prevent evaluator bias
- Flag when scope doesn't match time budget
"""

def build_prompt(instruction: str) -> str:
    return f"{SYSTEM_CONTEXT}\n\n{instruction}"
```

**JSON Schema Definition:**
```python
# Example schema for scope generation
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
    "required": ["title", "business_context", "must_have_requirements", 
                 "nice_to_have_requirements", "constraints"]
}
```

### 6.4 Rate Limiting & Retry Logic

**Gemini API Limits:**
- Free tier: 15 RPM (requests per minute)
- Paid tier: 1,000 RPM
- Rate limit errors return 429 status

**Retry Strategy:**
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class RateLimitError(Exception):
    pass

@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_gemini_with_retry(client: GeminiClient, prompt: str) -> dict:
    """Call Gemini with exponential backoff retry."""
    try:
        return client.generate_json(prompt)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            raise RateLimitError(f"Rate limit exceeded: {e}")
        raise
```

---

## 7. MVP Implementation Plan

### 7.1 Week 1: Core Generator

**Day 1-2: Setup**
- Initialize FastAPI project structure
- Set up Gemini API integration with google-generativeai SDK
- Create input/output models (Pydantic)
- Configure environment variables and secrets

**Day 3-4: Generation Pipeline**
- Implement 4-phase pipeline (extract → scope → validate → rubric)
- Add quality gates with validation logic
- Build GeminiClient wrapper class
- Implement JSON schema validation

**Day 5: Testing**
- Test with 5 different job descriptions (backend, frontend, full-stack, data, mobile)
- Validate time estimates are realistic
- Check rubric quality and consistency
- Measure generation latency

**Deliverable:** Working API endpoint that generates assignments in ~60-90 seconds

### 7.2 Week 2: Scope Validator

**Day 1-2: Self-Critique Logic**
- Agent reviews its own output
- Flags time mismatches (±15% tolerance)
- Identifies missing business context
- Validates rubric weights sum to 1.0

**Day 3-4: Refinement Loop**
- Implement adjustment logic for iterative improvements
- Add feedback endpoint for user corrections
- Test refinement with edge cases
- Add logging for refinement patterns

**Day 5: Edge Case Handling**
- Vague job descriptions → request clarification
- Unrealistic scope → suggest alternatives
- Mismatched seniority → warn user
- Missing tech stack → infer from job description

**Deliverable:** Validation system that catches 90%+ of bad assignments

### 7.3 Week 3: Frontend + Polish

**Day 1-3: UI Development**
- React form for input (multi-step wizard)
- Markdown display for output with syntax highlighting
- Download artifacts (Markdown, PDF via ReportLab)
- Loading states with progress indicators

**Day 4: Quality Checks**
- Semantic check: Does assignment reflect job responsibilities?
- Clarity check: Is business context understandable?
- Rubric quality check: Can it be applied consistently?
- Add example assignments for reference

**Day 5: Documentation**
- API documentation (OpenAPI/Swagger)
- User guide with screenshots
- Example outputs for 5 different roles
- README with setup instructions

**Deliverable:** Usable web interface with documentation

---

## 8. Technical Considerations

### 8.1 Error Handling

```python
class GenerationError(Exception):
    """Base exception for generation failures"""

class ScopeValidationError(GenerationError):
    """Scope doesn't match time budget"""
    
class ContextExtractionError(GenerationError):
    """Can't extract meaningful context from job description"""
    
class RubricGenerationError(GenerationError):
    """Can't create consistent evaluation criteria"""

class GeminiAPIError(GenerationError):
    """Gemini API failure"""

# Usage in API endpoint:
@app.post("/api/v1/assignments/generate")
async def generate_assignment(input: AssignmentInput):
    try:
        assignment = await generate_assignment_pipeline(input)
        return assignment
    except ScopeValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "scope_mismatch",
                "message": str(e),
                "suggestion": "Reduce requirements or increase time budget"
            }
        )
    except ContextExtractionError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "insufficient_context",
                "message": str(e),
                "suggestion": "Provide more details in job description"
            }
        )
    except GeminiAPIError as e:
        logger.error("gemini_api_error", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "AI service temporarily unavailable"
            }
        )
```

### 8.2 Observability

**Logging:**
```python
import structlog

logger = structlog.get_logger()

# Log each pipeline phase
logger.info(
    "phase_completed",
    phase="context_extraction",
    duration_seconds=duration,
    responsibilities_found=len(context.responsibilities),
    business_domain=context.business_domain
)

logger.info(
    "assignment_generated",
    assignment_id=assignment.assignment_id,
    duration_seconds=total_duration,
    seniority=input.seniority_level,
    time_budget_hours=input.time_budget_hours,
    validation_passed=validation.passed,
    scope_warnings=len(assignment.scope_warnings)
)
```

**Metrics to Track:**
- Generation success rate
- Average generation time per phase
- Validation failure reasons (for improvement)
- Gemini API latency
- Token usage per request

### 8.3 Performance Optimization

**Caching Strategy:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_context_for_job_description(job_description_hash: str) -> JobContext:
    """Cache context extraction for identical job descriptions."""
    # Implementation
    pass

# Use content-based hashing
import hashlib

def hash_job_description(jd: str) -> str:
    return hashlib.sha256(jd.encode()).hexdigest()[:16]
```

**Parallel Processing:**
```python
import asyncio

async def generate_assignment_parallel(input: AssignmentInput):
    """Run independent phases in parallel where possible."""
    
    # Phase 1: Context extraction (blocking)
    context = await extract_context(input)
    
    # Phase 2 & 3: Scope definition and initial validation can overlap
    scope_task = asyncio.create_task(define_scope(context, input))
    
    scope = await scope_task
    validation = await validate_scope(scope, input)
    
    if not validation.passed:
        raise ScopeValidationError(validation.issues)
    
    # Phase 4: Rubric generation
    rubric = await generate_rubric(scope, input)
    
    return assemble_assignment(context, scope, rubric, validation)
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# Test input validation
def test_assignment_input_validation():
    # Valid input
    valid_input = AssignmentInput(
        job_title="Backend Engineer",
        job_description="Build scalable APIs...",
        tech_stack=["Python", "FastAPI"],
        time_budget_hours=4.0,
        seniority_level="senior",
        must_evaluate=["API design"]
    )
    assert valid_input.time_budget_hours == 4.0
    
    # Invalid time budget
    with pytest.raises(ValidationError):
        AssignmentInput(
            job_title="Backend Engineer",
            job_description="Build APIs...",
            tech_stack=["Python"],
            time_budget_hours=15.0,  # Too high
            seniority_level="senior",
            must_evaluate=[]
        )

# Test quality gates
def test_time_validation():
    scope = create_test_scope(total_minutes=300)
    result = QualityGate().validate_scope(scope, time_budget=4.0)
    assert result.passed  # 300 min ≈ 5h, within 15% of 4h * 60 = 240
    
def test_rubric_weight_validation():
    rubric = [
        RubricItem(area="API Design", weight=0.4, ...),
        RubricItem(area="Error Handling", weight=0.35, ...),
        RubricItem(area="Testing", weight=0.25, ...)
    ]
    result = QualityGate().validate_rubric(rubric)
    assert result.passed  # Weights sum to 1.0
```

### 9.2 Integration Tests

```python
@pytest.mark.integration
async def test_full_generation_pipeline():
    """Test complete assignment generation with Gemini."""
    input = AssignmentInput(
        job_title="Senior Backend Engineer",
        job_description="""
        Join our fintech team building payroll infrastructure.
        You'll work on SEPA integrations, handle complex tax calculations,
        and build admin tools for HR teams. 
        Tech: Python, FastAPI, PostgreSQL, Redis.
        """,
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
        time_budget_hours=4.0,
        seniority_level="senior",
        must_evaluate=["API design", "error handling", "data modeling"]
    )
    
    result = await generate_assignment_pipeline(input)
    
    # Validate output structure
    assert result.candidate_brief is not None
    assert result.evaluator_guide is not None
    assert result.time_breakdown is not None
    
    # Validate time breakdown
    assert result.time_breakdown.total_minutes <= 270  # 4.5h max
    assert result.time_breakdown.breakdown_valid
    
    # Validate business context
    assert "payroll" in result.candidate_brief.business_context.lower()
    assert len(result.candidate_brief.business_context) >= 200
    
    # Validate rubric
    assert len(result.evaluator_guide.scoring_rubric) >= 3
    rubric_weights = sum(item.weight for item in result.evaluator_guide.scoring_rubric)
    assert abs(rubric_weights - 1.0) < 0.01
    
    # Validate requirements
    assert len(result.candidate_brief.requirements.must_have) >= 3
    assert all(
        req.estimated_time_minutes > 0 
        for req in result.candidate_brief.requirements.must_have
    )

@pytest.mark.integration
async def test_refinement_workflow():
    """Test assignment refinement based on feedback."""
    # Generate initial assignment
    initial = await generate_assignment_pipeline(base_input)
    
    # Request refinement
    feedback = RefinementFeedback(
        assignment_id=initial.assignment_id,
        changes=[
            Change(type="adjust_time", description="Reduce to 3 hours"),
            Change(type="add_requirement", description="Add logging/observability")
        ]
    )
    
    refined = await refine_assignment(initial, feedback)
    
    # Validate refinement
    assert refined.time_breakdown.total_minutes <= 210  # 3.5h max
    assert any(
        "observability" in req.description.lower() or "logging" in req.description.lower()
        for req in refined.candidate_brief.requirements.must_have
    )
```

### 9.3 Quality Assurance

**Manual Review Checklist:**
```python
class AssignmentQualityChecklist:
    """Manual QA checklist for generated assignments."""
    
    @staticmethod
    def check_business_context(assignment: GeneratedAssignment) -> bool:
        """Is business context specific, not generic?"""
        generic_terms = ["bookstore", "todo app", "blog", "e-commerce"]
        context = assignment.candidate_brief.business_context.lower()
        return not any(term in context for term in generic_terms)
    
    @staticmethod
    def check_requirements_testable(assignment: GeneratedAssignment) -> bool:
        """Are requirements concrete and testable?"""
        vague_terms = ["improve", "enhance", "optimize", "make better"]
        requirements = [
            req.description.lower() 
            for req in assignment.candidate_brief.requirements.must_have
        ]
        return not any(
            any(term in req for term in vague_terms)
            for req in requirements
        )
    
    @staticmethod
    def check_time_breakdown(assignment: GeneratedAssignment) -> bool:
        """Does time breakdown sum correctly?"""
        breakdown = assignment.time_breakdown
        expected_total = (
            breakdown.setup_minutes +
            breakdown.core_implementation_minutes +
            breakdown.testing_minutes +
            breakdown.documentation_minutes +
            breakdown.buffer_minutes
        )
        return abs(breakdown.total_minutes - expected_total) < 5
```

---

## 10. Post-MVP Features

### 10.1 Phase 2: Template Library (Weeks 4-5)
- Save generated assignments as reusable templates
- Search templates by role, seniority, tech stack, industry
- Community-contributed templates with ratings
- Template versioning and iteration tracking

### 10.2 Phase 3: Candidate Experience (Weeks 6-8)
- Public preview page (candidates see assignment before applying)
- Time tracking integration (actual vs estimated)
- Submission portal with file upload
- Automated acknowledgment emails

### 10.3 Phase 4: Analytics Dashboard (Weeks 9-10)
- Track completion rates by assignment type
- Identify bottleneck requirements (which take longest)
- A/B test different scope approaches
- Evaluator consistency metrics

### 10.4 Phase 5: Multi-language Support (Week 11)
- German localization for Berlin market
- Support for EU languages (French, Spanish, Dutch)
- Locale-specific business context examples

---

## 11. Open Questions & Decisions

### 11.1 Output Format
**Question:** Markdown only, or also PDF/DOCX?

**Decision:** 
- Primary: Markdown (easy to edit, version control friendly)
- Secondary: PDF export via ReportLab (for formal distribution)
- Future: DOCX via python-docx (if demand exists)

**Rationale:** Markdown satisfies 80% of use cases, PDF for professional sharing.

### 11.2 Storage Strategy
**Question:** Store generated assignments in database or generate on-demand?

**Decision (MVP):** 
- Generate on-demand, no persistence
- Return assignment_id for session tracking only
- Cache job description hashes to avoid re-extraction

**Decision (Post-MVP):**
- Store in PostgreSQL with user accounts
- Enable template library and sharing features

**Rationale:** Reduce complexity for MVP, add storage when user accounts exist.

### 11.3 Pricing Model
**Question:** Free, freemium, or usage-based?

**Decision:**
- Free tier: 5 generations per month
- Pro tier: $29/month for unlimited generations
- Enterprise: Custom pricing for team features

**Rationale:** Gemini costs are negligible (~$0.003/generation), capture value through convenience.

### 11.4 Evaluation Automation
**Question:** Build tools to help evaluators score submissions?

**Decision:** Phase 4 feature (post-MVP)

**Rationale:** Focus on generation quality first, evaluation assistance requires submission management system.

---

## 12. Success Criteria

### 12.1 Week 1 Success Metrics
- Generate 10 assignments from different job descriptions
- 8/10 have realistic time estimates (validated manually)
- 8/10 have clear, specific business context (not generic)
- Average generation time < 90 seconds
- Zero Gemini API failures

### 12.2 Week 2 Success Metrics
- Validation catches 90%+ of scope issues in test suite
- Refinement loop improves assignments in 1-2 iterations
- Quality gates prevent 100% of impossible time budgets
- Documentation covers all edge cases

### 12.3 Week 3 Success Metrics
- Non-technical user can generate assignment in <5 minutes
- Output artifacts require no editing for 70% of use cases
- Positive feedback from 3+ hiring managers
- Frontend handles errors gracefully with helpful messages
- Documentation includes 5+ example outputs

---

## 13. Repository Structure

```
take-home-generator/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # FastAPI endpoints
│   │   ├── schemas.py             # Pydantic models
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── generator.py           # Main generation pipeline
│   │   ├── validator.py           # Scope validation logic
│   │   ├── quality_gates.py       # Quality check implementations
│   │   └── prompts.py             # Prompt templates
│   ├── clients/
│   │   ├── __init__.py
│   │   └── gemini_client.py       # Gemini API wrapper
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── time_estimator.py      # Time calculation utilities
│   │   └── logger.py              # Structured logging setup
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_generator.py
│   │   ├── test_validator.py
│   │   ├── test_quality_gates.py
│   │   └── fixtures/              # Sample job descriptions
│   ├── main.py                    # FastAPI app entry point
│   └── config.py                  # Configuration management
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm.tsx      # Multi-step form
│   │   │   ├── OutputDisplay.tsx  # Markdown renderer
│   │   │   └── LoadingState.tsx   # Progress indicators
│   │   ├── api/
│   │   │   └── client.ts          # Backend API client
│   │   ├── types/
│   │   │   └── assignment.ts      # TypeScript interfaces
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
├── examples/
│   └── sample_assignments/
│       ├── backend_senior.md
│       ├── frontend_mid.md
│       ├── fullstack_staff.md
│       ├── data_engineer.md
│       └── mobile_junior.md
├── docs/
│   ├── api.md                     # API documentation
│   ├── user_guide.md              # How to use the tool
│   └── examples.md                # Reference outputs
├── scripts/
│   └── generate_sample.py         # CLI for testing
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 14. Dependencies

### 14.1 Backend Requirements

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Gemini API
google-generativeai==0.3.2

# Utilities
python-dotenv==1.0.0
tenacity==8.2.3          # Retry logic
structlog==23.2.0        # Structured logging

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2            # For testing FastAPI

# Development
black==23.12.0
ruff==0.1.8
mypy==1.7.1
```

### 14.2 Frontend Requirements

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^9.0.0",
    "axios": "^1.6.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## 15. Next Steps for Claude Code

### 15.1 Immediate Actions (Day 1)

1. **Project Setup**
   ```bash
   mkdir take-home-generator
   cd take-home-generator
   mkdir -p backend/{api,core,clients,utils,tests}
   touch backend/main.py backend/config.py
   ```

2. **Environment Configuration**
   ```bash
   # .env.example
   GEMINI_API_KEY=your_api_key_here
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```

3. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn google-generativeai pydantic python-dotenv
   ```

4. **Verify Gemini API**
   ```python
   # Test script to verify API access
   import google.generativeai as genai
   import os
   
   genai.configure(api_key=os.environ["GEMINI_API_KEY"])
   model = genai.GenerativeModel("gemini-2.5-flash-preview-05-21")
   response = model.generate_content("Hello, world!")
   print(response.text)
   ```

### 15.2 Implementation Order

**Priority 1: Core Generation (Days 1-3)**
- Implement Pydantic schemas from Section 3
- Build GeminiClient wrapper (Section 6.2)
- Create 4-phase pipeline (Section 4.1)
- Add basic error handling

**Priority 2: Validation (Days 4-5)**
- Implement QualityGate class (Section 4.2)
- Add time validation logic
- Create validation endpoint

**Priority 3: API Endpoints (Day 6)**
- FastAPI routes (Section 5.1)
- Request/response handling
- Error responses

**Priority 4: Testing (Day 7)**
- Unit tests for quality gates
- Integration tests with sample job descriptions
- Mock Gemini responses for fast tests

### 15.3 Prompt for Claude Code

```
Build a FastAPI backend for an AI-powered take-home assignment generator:

CONTEXT:
- Uses Google Gemini Flash 2.5 API for generation
- Takes job descriptions and generates scoped coding assignments
- Includes time breakdowns, evaluation rubrics, and business context

REQUIREMENTS:
1. Implement data models from Section 3 using Pydantic
2. Create GeminiClient wrapper (Section 6.2) with:
   - JSON structured output support
   - Retry logic with exponential backoff
   - Error handling for rate limits
3. Build 4-phase generation pipeline (Section 4.1):
   - Context extraction
   - Scope definition
   - Validation
   - Rubric generation
4. Add quality gates (Section 4.2) for:
   - Time estimate validation (±15%)
   - Business context quality
   - Rubric weight validation
5. Create FastAPI endpoints (Section 5.1):
   - POST /api/v1/assignments/generate
   - POST /api/v1/assignments/validate
6. Include comprehensive error handling (Section 8.1)
7. Add structured logging with duration tracking

TECHNICAL STACK:
- Python 3.11+
- FastAPI
- google-generativeai SDK
- Pydantic for validation

Use the schemas, quality gates, and prompting strategies defined in the spec.
Include pytest tests for the generation pipeline with sample job descriptions.
```

---

## 16. Risk Assessment & Mitigation

### 16.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API instability | Medium | High | Implement retry logic, fallback to cached responses |
| JSON parsing failures | Medium | Medium | Add schema validation, provide format examples in prompts |
| Time estimates inaccurate | High | Medium | Iterative calibration with real candidate data |
| Quality inconsistency | Medium | High | Quality gates, validation pipeline, example-driven prompts |

### 16.2 Product Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Assignments still too generic | Medium | High | Strong emphasis on business context in prompts, validation checks |
| Users don't trust AI output | High | Medium | Show reasoning, allow refinement, provide examples |
| Time estimates still wrong | High | High | Conservative estimates, explicit buffers, iterative learning |
| Market fit unclear | Medium | High | Early user testing with 10+ hiring managers |

---

This spec provides everything Claude Code needs to build a production-ready MVP using Gemini Flash 2.5 instead of Claude API, with comprehensive technical details, implementation guidance, and quality assurance strategies.