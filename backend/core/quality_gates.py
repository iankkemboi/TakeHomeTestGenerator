"""
Quality gates for validating generated assignments.
"""

from typing import List
from backend.api.schemas import (
    JobContext,
    AssignmentScope,
    RubricItem,
    ValidationResult
)


class QualityGate:
    """
    Quality gates to ensure generated assignments meet quality standards.
    """

    def validate_context_extraction(self, context: JobContext) -> ValidationResult:
        """
        Validate that context extraction is sufficient.

        Args:
            context: Extracted job context

        Returns:
            ValidationResult with pass/fail and issues
        """
        issues = []
        warnings = []

        # Check responsibilities
        if len(context.responsibilities) < 3:
            issues.append("Insufficient responsibilities extracted (minimum 3 required)")

        # Check business domain
        if not context.business_domain or len(context.business_domain.strip()) == 0:
            issues.append("Business domain not identified")

        # Check daily technologies
        if not context.daily_technologies or len(context.daily_technologies) == 0:
            issues.append("Daily technologies not specified")

        # Warnings for missing optional fields
        if not context.collaboration_patterns:
            warnings.append("Collaboration patterns not identified (optional)")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def validate_scope(
        self,
        scope: AssignmentScope,
        time_budget_hours: float
    ) -> ValidationResult:
        """
        Validate that assignment scope is realistic.

        Args:
            scope: Assignment scope
            time_budget_hours: Target time budget in hours

        Returns:
            ValidationResult with pass/fail and issues
        """
        issues = []
        warnings = []

        # Calculate total time from requirements
        total_time = sum(req.estimated_time_minutes for req in scope.all_requirements)
        expected_minutes = time_budget_hours * 60
        time_ratio = total_time / expected_minutes

        # Time budget validation (+/-25% tolerance)
        if not (0.75 <= time_ratio <= 1.25):
            issues.append(
                f"Time mismatch: requirements sum to {total_time} minutes "
                f"but budget is {expected_minutes} minutes (ratio: {time_ratio:.2f}). "
                f"Should be within +/-25% of budget."
            )

        # Business context validation
        if len(scope.business_context) < 100:
            issues.append(
                f"Business context too brief ({len(scope.business_context)} chars, "
                f"minimum 100 required)"
            )

        if len(scope.business_context) > 2000:
            warnings.append(
                f"Business context quite long ({len(scope.business_context)} chars, "
                f"recommended maximum 2000)"
            )

        # Requirements count validation
        if len(scope.must_have) < 3:
            issues.append(f"Too few must-have requirements ({len(scope.must_have)}, minimum 3)")

        if len(scope.must_have) > 7:
            warnings.append(
                f"Many must-have requirements ({len(scope.must_have)}). "
                f"Consider moving some to nice-to-have."
            )

        # Constraints validation
        if len(scope.constraints) < 2:
            warnings.append(
                f"Few constraints specified ({len(scope.constraints)}). "
                f"Consider adding more realistic constraints."
            )

        # Check for generic business context
        generic_terms = ["bookstore", "todo", "to-do", "blog", "e-commerce store"]
        context_lower = scope.business_context.lower()
        for term in generic_terms:
            if term in context_lower:
                warnings.append(
                    f"Business context may be too generic (contains '{term}'). "
                    f"Ensure it reflects specific job responsibilities."
                )
                break

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def validate_rubric(self, rubric: List[RubricItem]) -> ValidationResult:
        """
        Validate evaluation rubric quality.

        Args:
            rubric: List of rubric items

        Returns:
            ValidationResult with pass/fail and issues
        """
        issues = []
        warnings = []

        # Check rubric count
        if len(rubric) < 3:
            issues.append(f"Too few rubric items ({len(rubric)}, minimum 3)")

        if len(rubric) > 7:
            warnings.append(
                f"Many rubric items ({len(rubric)}). "
                f"Consider consolidating for easier evaluation."
            )

        # Validate weights sum to 1.0
        weight_sum = sum(item.weight for item in rubric)
        if abs(weight_sum - 1.0) > 0.01:
            issues.append(
                f"Rubric weights sum to {weight_sum:.3f}, must be 1.0 (+/-0.01)"
            )

        # Check for zero or negative weights
        for item in rubric:
            if item.weight <= 0:
                issues.append(
                    f"Rubric item '{item.area}' has invalid weight {item.weight} "
                    f"(must be > 0)"
                )

        # Check for very small weights
        for item in rubric:
            if 0 < item.weight < 0.05:
                warnings.append(
                    f"Rubric item '{item.area}' has very small weight {item.weight} "
                    f"(< 5%). Consider removing or increasing weight."
                )

        # Validate expectations are not empty
        for item in rubric:
            if not item.junior_expectation or not item.junior_expectation.strip():
                warnings.append(f"Rubric item '{item.area}' has empty junior expectation")
            if not item.mid_expectation or not item.mid_expectation.strip():
                warnings.append(f"Rubric item '{item.area}' has empty mid expectation")
            if not item.senior_expectation or not item.senior_expectation.strip():
                warnings.append(f"Rubric item '{item.area}' has empty senior expectation")
            if not item.scoring_guide or not item.scoring_guide.strip():
                issues.append(f"Rubric item '{item.area}' has empty scoring guide")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def check_seniority_match(
        self,
        scope: AssignmentScope,
        seniority_level: str
    ) -> bool:
        """
        Check if assignment complexity matches seniority level.

        This is a heuristic check based on:
        - Number of requirements
        - Total time budget
        - Complexity indicators in requirements

        Args:
            scope: Assignment scope
            seniority_level: Target seniority level

        Returns:
            True if match seems appropriate
        """
        requirement_count = len(scope.must_have)
        total_time = sum(req.estimated_time_minutes for req in scope.all_requirements)

        # Heuristic thresholds
        if seniority_level == "junior":
            # Juniors: 3-4 requirements, 2-3 hours
            return 3 <= requirement_count <= 4 and 120 <= total_time <= 240

        elif seniority_level == "mid":
            # Mid: 4-5 requirements, 3-4 hours
            return 4 <= requirement_count <= 5 and 180 <= total_time <= 300

        elif seniority_level == "senior":
            # Senior: 5-6 requirements, 4-6 hours
            return 5 <= requirement_count <= 6 and 240 <= total_time <= 420

        elif seniority_level == "staff":
            # Staff: 6-7 requirements, 6-8 hours
            return 6 <= requirement_count <= 7 and 360 <= total_time <= 540

        return True  # Unknown level, skip check

    def generate_scope_warnings(
        self,
        scope: AssignmentScope,
        seniority_level: str,
        time_budget_hours: float
    ) -> List[str]:
        """
        Generate warnings about potential scope issues.

        Args:
            scope: Assignment scope
            seniority_level: Target seniority level
            time_budget_hours: Time budget in hours

        Returns:
            List of warning messages
        """
        warnings = []

        # Check seniority match
        if not self.check_seniority_match(scope, seniority_level):
            warnings.append(
                f"Assignment complexity may not match {seniority_level} level. "
                f"Consider adjusting number of requirements or time budget."
            )

        # Check requirement balance
        must_have_count = len(scope.must_have)
        nice_to_have_count = len(scope.nice_to_have)

        if must_have_count > 6:
            warnings.append(
                f"Many must-have requirements ({must_have_count}). "
                f"Candidates may struggle to complete all within time budget."
            )

        if nice_to_have_count == 0:
            warnings.append(
                "No nice-to-have requirements. Consider adding optional features "
                "to differentiate exceptional candidates."
            )

        # Check time distribution
        must_have_time = sum(req.estimated_time_minutes for req in scope.must_have)
        total_time = sum(req.estimated_time_minutes for req in scope.all_requirements)

        if total_time > 0:
            must_have_ratio = must_have_time / total_time
            if must_have_ratio < 0.5:
                warnings.append(
                    f"Must-have requirements only account for {must_have_ratio:.0%} of time. "
                    f"Consider moving some nice-to-have items to must-have."
                )

        return warnings
