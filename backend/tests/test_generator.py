"""
Tests for the assignment generator.
"""

import pytest
from backend.api.schemas import (
    AssignmentInput,
    JobContext,
    AssignmentScope,
    Requirement
)
from backend.core.quality_gates import QualityGate


class TestQualityGates:
    """Test quality gate validations."""

    def test_context_validation_success(self):
        """Test successful context validation."""
        gate = QualityGate()
        context = JobContext(
            responsibilities=["Build APIs", "Design databases", "Write tests"],
            business_domain="Fintech - Payroll processing",
            daily_technologies=["Python", "FastAPI", "PostgreSQL"],
            collaboration_patterns="Agile team with daily standups"
        )

        result = gate.validate_context_extraction(context)
        assert result.passed
        assert len(result.issues) == 0

    def test_context_validation_missing_responsibilities(self):
        """Test context validation with insufficient responsibilities."""
        gate = QualityGate()
        context = JobContext(
            responsibilities=["Build APIs"],  # Only 1, need 3+
            business_domain="Fintech",
            daily_technologies=["Python"]
        )

        result = gate.validate_context_extraction(context)
        assert not result.passed
        assert any("responsibilities" in issue.lower() for issue in result.issues)

    def test_scope_validation_time_mismatch(self):
        """Test scope validation with time mismatch."""
        gate = QualityGate()
        scope = AssignmentScope(
            title="Test Assignment",
            business_context="A" * 250,  # Valid length
            must_have=[
                Requirement(
                    description="Feature 1",
                    estimated_time_minutes=60,
                    why_it_matters="Important"
                )
            ],
            nice_to_have=[],
            constraints=["Rate limit: 100 req/min"]
        )

        # 60 minutes but budget is 240 (4 hours) - ratio 0.25, outside Â+/-15%
        result = gate.validate_scope(scope, time_budget_hours=4.0)
        assert not result.passed
        assert any("time mismatch" in issue.lower() for issue in result.issues)

    def test_scope_validation_success(self):
        """Test successful scope validation."""
        gate = QualityGate()
        scope = AssignmentScope(
            title="Payment Processing API",
            business_context="Build a payment processing system for our fintech platform. " * 5,
            must_have=[
                Requirement(
                    description="Create payment endpoint",
                    estimated_time_minutes=80,
                    why_it_matters="Core functionality"
                ),
                Requirement(
                    description="Add webhook handling",
                    estimated_time_minutes=60,
                    why_it_matters="Real-time updates"
                ),
                Requirement(
                    description="Implement idempotency",
                    estimated_time_minutes=70,
                    why_it_matters="Prevent duplicate payments"
                )
            ],
            nice_to_have=[
                Requirement(
                    description="Add retry logic",
                    estimated_time_minutes=30,
                    why_it_matters="Reliability"
                )
            ],
            constraints=["Rate limit: 100 req/min", "Max payload: 1MB"]
        )

        # Total: 240 minutes = 4 hours
        result = gate.validate_scope(scope, time_budget_hours=4.0)
        assert result.passed
        assert len(result.issues) == 0

    def test_rubric_validation_weights_sum(self):
        """Test rubric validation with incorrect weight sum."""
        from backend.api.schemas import RubricItem

        gate = QualityGate()
        rubric = [
            RubricItem(
                area="API Design",
                weight=0.3,
                junior_expectation="Basic endpoints",
                mid_expectation="RESTful design",
                senior_expectation="Advanced patterns",
                scoring_guide="1-5 scale"
            ),
            RubricItem(
                area="Error Handling",
                weight=0.3,  # Sum = 0.6, not 1.0
                junior_expectation="Basic try/catch",
                mid_expectation="Proper error codes",
                senior_expectation="Comprehensive handling",
                scoring_guide="1-5 scale"
            )
        ]

        result = gate.validate_rubric(rubric)
        assert not result.passed
        assert any("weight" in issue.lower() for issue in result.issues)

    def test_seniority_match_senior(self):
        """Test seniority matching for senior level."""
        gate = QualityGate()
        scope = AssignmentScope(
            title="Test",
            business_context="A" * 250,
            must_have=[
                Requirement(description=f"Req {i}", estimated_time_minutes=60, why_it_matters="Test")
                for i in range(5)
            ],
            nice_to_have=[],
            constraints=[]
        )

        # 5 requirements, 300 minutes = senior level
        assert gate.check_seniority_match(scope, "senior")


class TestAssignmentInput:
    """Test AssignmentInput validation."""

    def test_valid_input(self):
        """Test valid assignment input."""
        input_data = AssignmentInput(
            job_title="Senior Backend Engineer",
            job_description="Build scalable APIs for our fintech platform. " * 30,
            tech_stack=["Python", "FastAPI", "PostgreSQL"],
            time_budget_hours=4.0,
            seniority_level="senior",
            must_evaluate=["API design", "error handling"]
        )

        assert input_data.job_title == "Senior Backend Engineer"
        assert input_data.time_budget_hours == 4.0
        assert input_data.seniority_level == "senior"

    def test_invalid_time_budget_too_low(self):
        """Test input with time budget too low."""
        with pytest.raises(Exception):  # Pydantic validation error
            AssignmentInput(
                job_title="Engineer",
                job_description="A" * 500,
                tech_stack=["Python"],
                time_budget_hours=1.0,  # Too low, min is 2.0
                seniority_level="mid"
            )

    def test_invalid_time_budget_too_high(self):
        """Test input with time budget too high."""
        with pytest.raises(Exception):  # Pydantic validation error
            AssignmentInput(
                job_title="Engineer",
                job_description="A" * 500,
                tech_stack=["Python"],
                time_budget_hours=10.0,  # Too high, max is 8.0
                seniority_level="mid"
            )

    def test_job_description_too_short(self):
        """Test input with job description too short."""
        with pytest.raises(Exception):  # Pydantic validation error
            AssignmentInput(
                job_title="Engineer",
                job_description="Short",  # Too short, min is 500 chars
                tech_stack=["Python"],
                time_budget_hours=4.0,
                seniority_level="mid"
            )
