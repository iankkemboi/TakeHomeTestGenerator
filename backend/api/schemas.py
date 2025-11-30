"""
Pydantic models for the Take-Home Test Generator API.
Defines input/output schemas for assignment generation.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Input Schemas
# ============================================================================

class AssignmentInput(BaseModel):
    """Input schema for generating a take-home assignment."""

    # Required Fields
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title (e.g., 'Senior Backend Engineer')")
    job_description: str = Field(..., min_length=100, max_length=5000, description="Full job description text")
    tech_stack: List[str] = Field(..., min_items=1, description="Technologies required (e.g., ['Python', 'FastAPI'])")
    time_budget_hours: float = Field(..., ge=2.0, le=8.0, description="Time budget in hours (2.0 to 8.0)")
    seniority_level: Literal["junior", "mid", "senior", "staff"] = Field(..., description="Target seniority level")

    # Optional Fields
    company_context: Optional[str] = Field(None, description="Company description and product domain")
    current_challenges: Optional[str] = Field(None, description="Team pain points or scaling issues")
    must_evaluate: List[str] = Field(default_factory=list, description="Skills that must be evaluated")
    avoid_topics: List[str] = Field(default_factory=list, description="Topics to avoid in the assignment")

    # Constraints
    candidate_can_use: Optional[List[str]] = Field(None, description="Allowed libraries/frameworks")
    submission_format: Literal["github", "zip", "codesandbox"] = Field(default="github", description="Submission format")


# ============================================================================
# Requirement Schemas
# ============================================================================

class Requirement(BaseModel):
    """Single requirement in the assignment."""
    description: str = Field(..., description="Clear description of what needs to be built")
    estimated_time_minutes: int = Field(..., gt=0, description="Time estimate in minutes")
    why_it_matters: str = Field(..., description="Why this requirement ties to actual job responsibilities")


class Requirements(BaseModel):
    """Collection of must-have and nice-to-have requirements."""
    must_have: List[Requirement] = Field(..., min_items=3, max_items=7, description="Core functionality")
    nice_to_have: List[Requirement] = Field(default_factory=list, description="Optional enhancements")
    constraints: List[str] = Field(default_factory=list, description="Technical constraints (rate limits, data volumes)")


# ============================================================================
# Candidate Brief Schemas
# ============================================================================

class CandidateBrief(BaseModel):
    """Assignment brief provided to candidates."""
    title: str = Field(..., description="Assignment title")
    business_context: str = Field(..., min_length=100, max_length=2000, description="Business context and problem statement")
    requirements: Requirements = Field(..., description="Must-have and nice-to-have requirements")
    submission_guidelines: str = Field(..., description="How to submit the assignment")
    evaluation_criteria: List[str] = Field(..., description="High-level evaluation areas")
    time_estimate: str = Field(..., description="Expected time (e.g., '3-4 hours')")


# ============================================================================
# Evaluator Guide Schemas
# ============================================================================

class RubricItem(BaseModel):
    """Single item in the evaluation rubric."""
    area: str = Field(..., description="Evaluation area (e.g., 'API Design')")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight in final score (0.0 to 1.0)")
    junior_expectation: str = Field(..., description="What to expect from junior candidates")
    mid_expectation: str = Field(..., description="What to expect from mid-level candidates")
    senior_expectation: str = Field(..., description="What to expect from senior candidates")
    scoring_guide: str = Field(..., description="How to assign 1-5 score for this area")


class EvaluatorGuide(BaseModel):
    """Guide for evaluating candidate submissions."""
    scoring_rubric: List[RubricItem] = Field(..., min_items=3, max_items=7, description="Evaluation rubric items")
    common_pitfalls: List[str] = Field(..., description="Common mistakes candidates make")
    red_flags: List[str] = Field(..., description="Indicators of poor understanding")
    green_flags: List[str] = Field(..., description="Indicators of strong performance")
    calibration_notes: str = Field(..., description="How to apply rubric consistently")

    @field_validator('scoring_rubric')
    @classmethod
    def validate_weights_sum_to_one(cls, v: List[RubricItem]) -> List[RubricItem]:
        """Ensure rubric weights sum to 1.0."""
        total_weight = sum(item.weight for item in v)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Rubric weights must sum to 1.0, got {total_weight}")
        return v


# ============================================================================
# Time Breakdown Schema
# ============================================================================

class TimeBreakdown(BaseModel):
    """Detailed time breakdown for the assignment."""
    total_minutes: int = Field(..., gt=0, description="Total estimated time in minutes")
    setup_minutes: int = Field(..., ge=0, description="Environment setup time")
    core_implementation_minutes: int = Field(..., gt=0, description="Core implementation time")
    testing_minutes: int = Field(..., ge=0, description="Testing time")
    documentation_minutes: int = Field(..., ge=0, description="Documentation time")
    buffer_minutes: int = Field(..., ge=0, description="Buffer time for unexpected issues")
    breakdown_valid: bool = Field(..., description="Whether breakdown components sum correctly")

    @field_validator('breakdown_valid')
    @classmethod
    def validate_breakdown_sum(cls, v: bool, info) -> bool:
        """Validate that breakdown components sum to total."""
        if not info.data:
            return v

        expected_total = (
            info.data.get('setup_minutes', 0) +
            info.data.get('core_implementation_minutes', 0) +
            info.data.get('testing_minutes', 0) +
            info.data.get('documentation_minutes', 0) +
            info.data.get('buffer_minutes', 0)
        )
        total = info.data.get('total_minutes', 0)

        # Allow 5 minute tolerance
        return abs(total - expected_total) < 5


# ============================================================================
# Output Schema
# ============================================================================

class GeneratedAssignment(BaseModel):
    """Complete generated assignment with all artifacts."""
    # Core Artifacts
    candidate_brief: CandidateBrief = Field(..., description="Brief for candidates")
    evaluator_guide: EvaluatorGuide = Field(..., description="Guide for evaluators")
    time_breakdown: TimeBreakdown = Field(..., description="Detailed time breakdown")

    # Metadata
    assignment_id: str = Field(..., description="Unique assignment identifier")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    estimated_difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Overall difficulty estimate")
    scope_warnings: List[str] = Field(default_factory=list, description="Warnings about scope mismatches")


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidationResult(BaseModel):
    """Result of validation checks."""
    passed: bool = Field(..., description="Whether validation passed")
    issues: List[str] = Field(default_factory=list, description="List of validation issues")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")


# ============================================================================
# Refinement Schemas
# ============================================================================

class Change(BaseModel):
    """Single change requested in refinement."""
    type: Literal["adjust_time", "add_requirement", "remove_requirement", "change_focus", "adjust_difficulty"]
    description: str = Field(..., min_length=1, description="Description of the change")


class RefinementFeedback(BaseModel):
    """Feedback for refining an assignment."""
    assignment_id: str = Field(..., description="Assignment to refine")
    changes: List[Change] = Field(..., min_items=1, description="List of requested changes")


# ============================================================================
# Internal Schemas (used in generation pipeline)
# ============================================================================

class JobContext(BaseModel):
    """Extracted context from job description."""
    responsibilities: List[str] = Field(..., description="Core technical responsibilities")
    business_domain: str = Field(..., description="Business domain and product context")
    daily_technologies: List[str] = Field(..., description="Technologies used daily")
    collaboration_patterns: Optional[str] = Field(None, description="Team collaboration patterns")


class AssignmentScope(BaseModel):
    """Defined scope for the assignment."""
    title: str
    business_context: str
    must_have: List[Requirement]
    nice_to_have: List[Requirement]
    constraints: List[str]

    @property
    def all_requirements(self) -> List[Requirement]:
        """Get all requirements (must-have + nice-to-have)."""
        return self.must_have + self.nice_to_have


class ScopeValidation(BaseModel):
    """Result of scope validation."""
    passed: bool
    issues: List[str]
    warnings: List[str]
