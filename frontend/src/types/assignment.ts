/**
 * TypeScript interfaces matching the backend Pydantic models
 */

export type SeniorityLevel = "junior" | "mid" | "senior" | "staff";
export type SubmissionFormat = "github" | "zip" | "codesandbox";
export type Difficulty = "easy" | "medium" | "hard";

// Input types
export interface AssignmentInput {
  job_title: string;
  job_description: string;
  tech_stack: string[];
  time_budget_hours: number;
  seniority_level: SeniorityLevel;
  company_context?: string;
  current_challenges?: string;
  must_evaluate: string[];
  avoid_topics: string[];
  candidate_can_use?: string[];
  submission_format: SubmissionFormat;
}

// Requirement types
export interface Requirement {
  description: string;
  estimated_time_minutes: number;
  why_it_matters: string;
}

export interface Requirements {
  must_have: Requirement[];
  nice_to_have: Requirement[];
  constraints: string[];
}

// Candidate brief
export interface CandidateBrief {
  title: string;
  business_context: string;
  requirements: Requirements;
  submission_guidelines: string;
  evaluation_criteria: string[];
  time_estimate: string;
}

// Rubric types
export interface RubricItem {
  area: string;
  weight: number;
  junior_expectation: string;
  mid_expectation: string;
  senior_expectation: string;
  scoring_guide: string;
}

export interface EvaluatorGuide {
  scoring_rubric: RubricItem[];
  common_pitfalls: string[];
  red_flags: string[];
  green_flags: string[];
  calibration_notes: string;
}

// Time breakdown
export interface TimeBreakdown {
  total_minutes: number;
  setup_minutes: number;
  core_implementation_minutes: number;
  testing_minutes: number;
  documentation_minutes: number;
  buffer_minutes: number;
  breakdown_valid: boolean;
}

// Output types
export interface GeneratedAssignment {
  candidate_brief: CandidateBrief;
  evaluator_guide: EvaluatorGuide;
  time_breakdown: TimeBreakdown;
  assignment_id: string;
  generated_at: string;
  estimated_difficulty: Difficulty;
  scope_warnings: string[];
}

// Validation result
export interface ValidationResult {
  passed: boolean;
  issues: string[];
  warnings: string[];
}

// API error response
export interface APIError {
  error: string;
  message: string;
  suggestion?: string;
}
