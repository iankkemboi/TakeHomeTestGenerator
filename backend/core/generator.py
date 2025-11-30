"""
Main generation pipeline for take-home assignments.
Implements 4-phase generation: context extraction, scope definition, validation, and rubric generation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

from backend.api.schemas import (
    AssignmentInput,
    GeneratedAssignment,
    CandidateBrief,
    EvaluatorGuide,
    TimeBreakdown,
    Requirements,
    Requirement,
    RubricItem,
    JobContext,
    AssignmentScope,
    ScopeValidation
)
from backend.clients.gemini_client import GeminiClient
from backend.core.prompts import (
    get_context_extraction_prompt,
    get_scope_definition_prompt,
    get_rubric_generation_prompt,
    get_time_breakdown_prompt,
    CONTEXT_SCHEMA,
    SCOPE_SCHEMA,
    RUBRIC_SCHEMA,
    TIME_BREAKDOWN_SCHEMA
)
from backend.core.quality_gates import QualityGate


class GenerationError(Exception):
    """Base exception for generation failures."""
    pass


class ScopeValidationError(GenerationError):
    """Scope doesn't match time budget."""
    pass


class ContextExtractionError(GenerationError):
    """Can't extract meaningful context from job description."""
    pass


class RubricGenerationError(GenerationError):
    """Can't create consistent evaluation criteria."""
    pass


class AssignmentGenerator:
    """
    Main class for generating take-home assignments.
    Orchestrates the 4-phase generation pipeline.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize generator.

        Args:
            gemini_client: Configured Gemini API client
        """
        self.client = gemini_client
        self.quality_gate = QualityGate()

    async def generate(self, input_data: AssignmentInput) -> GeneratedAssignment:
        """
        Generate a complete take-home assignment.

        Args:
            input_data: Assignment input parameters

        Returns:
            Generated assignment with all artifacts

        Raises:
            GenerationError: If generation fails at any phase
        """
        # Phase 1: Extract context
        context = await self._extract_context(input_data)

        # Phase 2: Define scope
        scope = await self._define_scope(context, input_data)

        # Phase 3: Validate scope
        validation = await self._validate_scope(scope, input_data)

        if not validation.passed:
            raise ScopeValidationError(
                f"Scope validation failed: {', '.join(validation.issues)}"
            )

        # Phase 4: Generate rubric and time breakdown
        rubric = await self._generate_rubric(scope, input_data)
        time_breakdown = await self._generate_time_breakdown(scope, input_data)

        # Assemble final assignment
        return self._assemble_assignment(
            context=context,
            scope=scope,
            rubric=rubric,
            time_breakdown=time_breakdown,
            validation=validation,
            input_data=input_data
        )

    async def _extract_context(self, input_data: AssignmentInput) -> JobContext:
        """
        Phase 1: Extract context from job description.

        Args:
            input_data: Assignment input

        Returns:
            Extracted job context

        Raises:
            ContextExtractionError: If context extraction fails
        """
        try:
            prompt = get_context_extraction_prompt(
                job_description=input_data.job_description,
                tech_stack=input_data.tech_stack
            )

            response = self.client.generate_json(prompt, schema=CONTEXT_SCHEMA)

            # Convert to JobContext
            context = JobContext(**response)

            # Validate context
            validation = self.quality_gate.validate_context_extraction(context)
            if not validation.passed:
                raise ContextExtractionError(
                    f"Context extraction validation failed: {', '.join(validation.issues)}"
                )

            return context

        except Exception as e:
            if isinstance(e, ContextExtractionError):
                raise
            raise ContextExtractionError(f"Failed to extract context: {e}")

    async def _define_scope(
        self,
        context: JobContext,
        input_data: AssignmentInput
    ) -> AssignmentScope:
        """
        Phase 2: Define assignment scope.

        Args:
            context: Extracted job context
            input_data: Assignment input

        Returns:
            Defined assignment scope

        Raises:
            GenerationError: If scope definition fails
        """
        try:
            prompt = get_scope_definition_prompt(
                context=context.model_dump(),
                seniority_level=input_data.seniority_level,
                time_budget_hours=input_data.time_budget_hours,
                must_evaluate=input_data.must_evaluate,
                avoid_topics=input_data.avoid_topics,
                company_context=input_data.company_context,
                current_challenges=input_data.current_challenges
            )

            response = self.client.generate_json(prompt, schema=SCOPE_SCHEMA)

            # Convert requirements to Requirement objects
            must_have = [Requirement(**req) for req in response["must_have_requirements"]]
            nice_to_have = [Requirement(**req) for req in response["nice_to_have_requirements"]]

            scope = AssignmentScope(
                title=response["title"],
                business_context=response["business_context"],
                must_have=must_have,
                nice_to_have=nice_to_have,
                constraints=response["constraints"]
            )

            return scope

        except Exception as e:
            raise GenerationError(f"Failed to define scope: {e}")

    async def _validate_scope(
        self,
        scope: AssignmentScope,
        input_data: AssignmentInput
    ) -> ScopeValidation:
        """
        Phase 3: Validate assignment scope.

        Args:
            scope: Assignment scope
            input_data: Assignment input

        Returns:
            Validation result
        """
        validation_result = self.quality_gate.validate_scope(
            scope=scope,
            time_budget_hours=input_data.time_budget_hours
        )

        warnings = self.quality_gate.generate_scope_warnings(
            scope=scope,
            seniority_level=input_data.seniority_level,
            time_budget_hours=input_data.time_budget_hours
        )

        # Combine warnings
        all_warnings = validation_result.warnings + warnings

        return ScopeValidation(
            passed=validation_result.passed,
            issues=validation_result.issues,
            warnings=all_warnings
        )

    async def _generate_rubric(
        self,
        scope: AssignmentScope,
        input_data: AssignmentInput
    ) -> EvaluatorGuide:
        """
        Phase 4a: Generate evaluation rubric.

        Args:
            scope: Assignment scope
            input_data: Assignment input

        Returns:
            Evaluator guide with rubric

        Raises:
            RubricGenerationError: If rubric generation fails
        """
        try:
            prompt = get_rubric_generation_prompt(
                scope=scope.model_dump(),
                seniority_level=input_data.seniority_level,
                must_evaluate=input_data.must_evaluate
            )

            response = self.client.generate_json(prompt, schema=RUBRIC_SCHEMA)

            # Convert to RubricItem objects
            rubric_items = [RubricItem(**item) for item in response["scoring_rubric"]]

            evaluator_guide = EvaluatorGuide(
                scoring_rubric=rubric_items,
                common_pitfalls=response["common_pitfalls"],
                red_flags=response["red_flags"],
                green_flags=response["green_flags"],
                calibration_notes=response["calibration_notes"]
            )

            # Validate rubric
            validation = self.quality_gate.validate_rubric(evaluator_guide.scoring_rubric)
            if not validation.passed:
                raise RubricGenerationError(
                    f"Rubric validation failed: {', '.join(validation.issues)}"
                )

            return evaluator_guide

        except Exception as e:
            if isinstance(e, RubricGenerationError):
                raise
            raise RubricGenerationError(f"Failed to generate rubric: {e}")

    async def _generate_time_breakdown(
        self,
        scope: AssignmentScope,
        input_data: AssignmentInput
    ) -> TimeBreakdown:
        """
        Phase 4b: Generate time breakdown.

        Args:
            scope: Assignment scope
            input_data: Assignment input

        Returns:
            Detailed time breakdown

        Raises:
            GenerationError: If time breakdown generation fails
        """
        try:
            prompt = get_time_breakdown_prompt(
                scope=scope.model_dump(),
                time_budget_hours=input_data.time_budget_hours
            )

            response = self.client.generate_json(prompt, schema=TIME_BREAKDOWN_SCHEMA)

            time_breakdown = TimeBreakdown(**response)

            return time_breakdown

        except Exception as e:
            raise GenerationError(f"Failed to generate time breakdown: {e}")

    def _assemble_assignment(
        self,
        context: JobContext,
        scope: AssignmentScope,
        rubric: EvaluatorGuide,
        time_breakdown: TimeBreakdown,
        validation: ScopeValidation,
        input_data: AssignmentInput
    ) -> GeneratedAssignment:
        """
        Assemble all components into final assignment.

        Args:
            context: Job context
            scope: Assignment scope
            rubric: Evaluator guide
            time_breakdown: Time breakdown
            validation: Validation result
            input_data: Original input

        Returns:
            Complete generated assignment
        """
        # Build candidate brief
        requirements = Requirements(
            must_have=scope.must_have,
            nice_to_have=scope.nice_to_have,
            constraints=scope.constraints
        )

        # Extract high-level criteria from rubric
        evaluation_criteria = [item.area for item in rubric.scoring_rubric]

        # Format time estimate
        hours = input_data.time_budget_hours
        if hours == int(hours):
            time_estimate = f"{int(hours)} hours"
        else:
            time_estimate = f"{hours:.1f} hours"

        # Build submission guidelines
        submission_guidelines = self._build_submission_guidelines(input_data)

        candidate_brief = CandidateBrief(
            title=scope.title,
            business_context=scope.business_context,
            requirements=requirements,
            submission_guidelines=submission_guidelines,
            evaluation_criteria=evaluation_criteria,
            time_estimate=time_estimate
        )

        # Determine difficulty
        difficulty = self._estimate_difficulty(scope, input_data)

        # Generate unique ID
        assignment_id = str(uuid.uuid4())

        return GeneratedAssignment(
            candidate_brief=candidate_brief,
            evaluator_guide=rubric,
            time_breakdown=time_breakdown,
            assignment_id=assignment_id,
            generated_at=datetime.now(),
            estimated_difficulty=difficulty,
            scope_warnings=validation.warnings
        )

    def _build_submission_guidelines(self, input_data: AssignmentInput) -> str:
        """
        Build submission guidelines based on format.

        Args:
            input_data: Assignment input

        Returns:
            Formatted submission guidelines
        """
        format_map = {
            "github": (
                "Please submit your solution as a GitHub repository. "
                "Include a comprehensive README with setup instructions, "
                "architecture decisions, and any assumptions made."
            ),
            "zip": (
                "Please submit your solution as a ZIP file. "
                "Include a comprehensive README with setup instructions, "
                "architecture decisions, and any assumptions made."
            ),
            "codesandbox": (
                "Please submit your solution as a CodeSandbox link. "
                "Ensure all dependencies are properly configured and the "
                "sandbox is publicly accessible."
            )
        }

        base_guidelines = format_map.get(input_data.submission_format, format_map["github"])

        additional_notes = []

        if input_data.candidate_can_use:
            libs = ", ".join(input_data.candidate_can_use)
            additional_notes.append(f"You may use the following libraries/frameworks: {libs}")

        if additional_notes:
            return base_guidelines + "\n\n" + " ".join(additional_notes)

        return base_guidelines

    def _estimate_difficulty(
        self,
        scope: AssignmentScope,
        input_data: AssignmentInput
    ) -> str:
        """
        Estimate assignment difficulty.

        Args:
            scope: Assignment scope
            input_data: Assignment input

        Returns:
            Difficulty level: easy, medium, or hard
        """
        # Heuristic based on time, requirements, and seniority
        total_time = sum(req.estimated_time_minutes for req in scope.all_requirements)
        requirement_count = len(scope.must_have)

        # Simple heuristic
        if total_time <= 180 and requirement_count <= 4:
            return "easy"
        elif total_time >= 360 or requirement_count >= 6:
            return "hard"
        else:
            return "medium"
