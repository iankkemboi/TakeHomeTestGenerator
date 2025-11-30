"""
FastAPI routes for the Take-Home Test Generator API.
"""

import time
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from backend.api.schemas import (
    AssignmentInput,
    GeneratedAssignment,
    ValidationResult
)
from backend.core.generator import (
    AssignmentGenerator,
    GenerationError,
    ScopeValidationError,
    ContextExtractionError,
    RubricGenerationError
)
from backend.clients.gemini_client import GeminiClient, GeminiAPIError
from backend.api.dependencies import get_generator
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["assignments"])


@router.post("/assignments/generate", response_model=GeneratedAssignment, status_code=201)
async def generate_assignment(
    input_data: AssignmentInput,
    generator: AssignmentGenerator = Depends(get_generator)
) -> GeneratedAssignment:
    """
    Generate a complete take-home assignment.

    Args:
        input_data: Assignment input parameters
        generator: Assignment generator dependency

    Returns:
        Generated assignment with all artifacts

    Raises:
        HTTPException: If generation fails
    """
    start_time = time.time()

    try:
        logger.info(
            "assignment_generation_started",
            job_title=input_data.job_title,
            seniority=input_data.seniority_level,
            time_budget_hours=input_data.time_budget_hours
        )

        # Generate assignment
        assignment = await generator.generate(input_data)

        duration = time.time() - start_time

        logger.info(
            "assignment_generated",
            assignment_id=assignment.assignment_id,
            duration_seconds=duration,
            seniority=input_data.seniority_level,
            difficulty=assignment.estimated_difficulty,
            warnings_count=len(assignment.scope_warnings)
        )

        return assignment

    except ScopeValidationError as e:
        logger.warning(
            "scope_validation_failed",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "scope_mismatch",
                "title": "Assignment scope needs adjustment",
                "message": "The AI-generated requirements don't quite match your time budget. This happens occasionally - the AI is being careful to create realistic assignments.",
                "technical_detail": str(e),
                "suggestions": [
                    "Click 'Try Again' to regenerate - results vary each time",
                    "Adjust your time budget slightly (try +/- 30 minutes)",
                    "Add more context in the job description to help the AI scope better"
                ]
            }
        )

    except ContextExtractionError as e:
        logger.warning(
            "context_extraction_failed",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "insufficient_context",
                "title": "Need more details",
                "message": "The job description doesn't have enough information to create a well-scoped assignment.",
                "technical_detail": str(e),
                "suggestions": [
                    "Add more details about the role's responsibilities",
                    "Include specific technical requirements or challenges",
                    "Describe the team structure or project context"
                ]
            }
        )

    except RubricGenerationError as e:
        logger.error(
            "rubric_generation_failed",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "rubric_generation_failed",
                "title": "Couldn't generate evaluation rubric",
                "message": "The AI had trouble creating the scoring rubric for this assignment.",
                "technical_detail": str(e),
                "suggestions": [
                    "Click 'Try Again' to regenerate",
                    "Try simplifying your requirements",
                    "If this persists, the AI service may be experiencing issues"
                ]
            }
        )

    except GeminiAPIError as e:
        logger.error(
            "gemini_api_error",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "title": "AI service temporarily unavailable",
                "message": "We're having trouble connecting to the AI service. This is usually temporary.",
                "suggestions": [
                    "Wait a moment and try again",
                    "Check if the issue persists after a few minutes"
                ]
            }
        )

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(
            "unexpected_error",
            error=str(e),
            error_type=type(e).__name__,
            traceback=error_traceback,
            duration_seconds=time.time() - start_time
        )
        # Include actual error in development for debugging
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "title": "Something went wrong",
                "message": f"An unexpected error occurred: {type(e).__name__}",
                "technical_detail": str(e),
                "suggestions": [
                    "Click 'Try Again' to retry",
                    "If this keeps happening, try refreshing the page"
                ]
            }
        )


@router.post("/assignments/validate", response_model=ValidationResult)
async def validate_assignment_input(
    input_data: AssignmentInput,
    generator: AssignmentGenerator = Depends(get_generator)
) -> ValidationResult:
    """
    Validate assignment input without generating full assignment.
    This is a quick check to see if the input will likely produce a good assignment.

    Args:
        input_data: Assignment input parameters
        generator: Assignment generator dependency

    Returns:
        Validation result

    Raises:
        HTTPException: If validation fails
    """
    start_time = time.time()

    try:
        logger.info(
            "assignment_validation_started",
            job_title=input_data.job_title
        )

        # Extract context only
        context = await generator._extract_context(input_data)

        # Quick scope check
        scope = await generator._define_scope(context, input_data)
        validation = await generator._validate_scope(scope, input_data)

        duration = time.time() - start_time

        logger.info(
            "assignment_validated",
            duration_seconds=duration,
            passed=validation.passed,
            issues_count=len(validation.issues),
            warnings_count=len(validation.warnings)
        )

        return ValidationResult(
            passed=validation.passed,
            issues=validation.issues,
            warnings=validation.warnings
        )

    except ContextExtractionError as e:
        logger.warning(
            "validation_context_extraction_failed",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "insufficient_context",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(
            "validation_unexpected_error",
            error=str(e),
            duration_seconds=time.time() - start_time
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "validation_failed",
                "message": "Validation failed unexpectedly"
            }
        )


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "take-home-test-generator"
    }
