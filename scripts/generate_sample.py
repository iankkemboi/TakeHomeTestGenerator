#!/usr/bin/env python3
"""
CLI script to test assignment generation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.schemas import AssignmentInput
from backend.clients.gemini_client import GeminiClient
from backend.core.generator import AssignmentGenerator
from backend.tests.fixtures.sample_job_description import BACKEND_SENIOR_JD


async def main():
    """Generate a sample assignment."""
    print("=== Take-Home Test Generator - Sample Generation ===\n")

    # Create input
    input_data = AssignmentInput(
        job_title="Senior Backend Engineer",
        job_description=BACKEND_SENIOR_JD,
        tech_stack=["Python", "FastAPI", "PostgreSQL", "Redis"],
        time_budget_hours=4.0,
        seniority_level="senior",
        must_evaluate=["API design", "error handling", "data modeling"],
        company_context="Fintech startup processing payroll for 10k+ companies",
        submission_format="github"
    )

    print(f"Job Title: {input_data.job_title}")
    print(f"Seniority: {input_data.seniority_level}")
    print(f"Time Budget: {input_data.time_budget_hours} hours")
    print(f"Tech Stack: {', '.join(input_data.tech_stack)}\n")

    # Create generator
    try:
        client = GeminiClient()
        generator = AssignmentGenerator(gemini_client=client)

        print("Generating assignment...\n")
        assignment = await generator.generate(input_data)

        print("=== GENERATION COMPLETE ===\n")
        print(f"Assignment ID: {assignment.assignment_id}")
        print(f"Difficulty: {assignment.estimated_difficulty}")
        print(f"Generated at: {assignment.generated_at}\n")

        print("=== CANDIDATE BRIEF ===")
        print(f"Title: {assignment.candidate_brief.title}")
        print(f"\nBusiness Context:\n{assignment.candidate_brief.business_context}\n")

        print("=== REQUIREMENTS ===")
        print("\nMust-Have:")
        for i, req in enumerate(assignment.candidate_brief.requirements.must_have, 1):
            print(f"\n{i}. {req.description}")
            print(f"   Time: {req.estimated_time_minutes} minutes")
            print(f"   Why: {req.why_it_matters}")

        if assignment.candidate_brief.requirements.nice_to_have:
            print("\nNice-to-Have:")
            for i, req in enumerate(assignment.candidate_brief.requirements.nice_to_have, 1):
                print(f"\n{i}. {req.description}")
                print(f"   Time: {req.estimated_time_minutes} minutes")

        print("\n=== TIME BREAKDOWN ===")
        tb = assignment.time_breakdown
        print(f"Total: {tb.total_minutes} minutes")
        print(f"  Setup: {tb.setup_minutes} min")
        print(f"  Implementation: {tb.core_implementation_minutes} min")
        print(f"  Testing: {tb.testing_minutes} min")
        print(f"  Documentation: {tb.documentation_minutes} min")
        print(f"  Buffer: {tb.buffer_minutes} min")

        print("\n=== EVALUATION RUBRIC ===")
        for item in assignment.evaluator_guide.scoring_rubric:
            print(f"\n{item.area} (weight: {item.weight})")
            print(f"  Senior expectation: {item.senior_expectation}")

        if assignment.scope_warnings:
            print("\n=== WARNINGS ===")
            for warning in assignment.scope_warnings:
                print(f"⚠️  {warning}")

        # Save to file
        output_file = Path("sample_assignment.json")
        with open(output_file, "w") as f:
            json.dump(assignment.model_dump(mode='json'), f, indent=2, default=str)

        print(f"\n✅ Full assignment saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
