/**
 * API client for communicating with the backend
 * Supports demo mode for frontend-only deployment
 */

import axios, { AxiosError } from 'axios';
import type { AssignmentInput, GeneratedAssignment, ValidationResult } from '../types/assignment';
import { generateDemoAssignment, simulateDelay } from './demoData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes (generation can take up to 90 seconds)
});

/**
 * Check if running in demo mode
 */
export function isDemoMode(): boolean {
  return DEMO_MODE;
}

/**
 * Generate a complete take-home assignment
 */
export async function generateAssignment(
  input: AssignmentInput
): Promise<GeneratedAssignment> {
  // Demo mode: simulate API response without backend
  if (DEMO_MODE) {
    console.log('🎭 Demo mode: Generating simulated assignment...');
    await simulateDelay(3000, 6000); // Simulate realistic API delay
    return generateDemoAssignment(input);
  }

  try {
    const response = await apiClient.post<GeneratedAssignment>(
      '/api/v1/assignments/generate',
      input
    );
    return response.data;
  } catch (error) {
    throw handleAPIError(error);
  }
}

/**
 * Validate assignment input without generating
 */
export async function validateAssignmentInput(
  input: AssignmentInput
): Promise<ValidationResult> {
  // Demo mode: always pass validation
  if (DEMO_MODE) {
    await simulateDelay(500, 1000);
    return {
      passed: true,
      issues: [],
      warnings: input.time_budget_hours < 2 
        ? ['Short time budget may limit scope'] 
        : [],
    };
  }

  try {
    const response = await apiClient.post<ValidationResult>(
      '/api/v1/assignments/validate',
      input
    );
    return response.data;
  } catch (error) {
    throw handleAPIError(error);
  }
}

/**
 * Check API health
 */
export async function healthCheck(): Promise<{ status: string; service: string }> {
  // Demo mode: always healthy
  if (DEMO_MODE) {
    return { status: 'healthy', service: 'demo-mode' };
  }

  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw handleAPIError(error);
  }
}

/**
 * Extended API error with friendly messages
 */
interface FriendlyAPIError {
  error: string;
  title?: string;
  message: string;
  technical_detail?: string;
  suggestions?: string[];
  suggestion?: string; // Legacy format
}

/**
 * Handle API errors and convert to user-friendly messages
 */
function handleAPIError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<FriendlyAPIError>;

    if (axiosError.response?.data) {
      const apiError = axiosError.response.data;
      
      // Build friendly error message
      let message = '';
      
      // Use title if available, otherwise use message
      if (apiError.title) {
        message = apiError.title;
        if (apiError.message) {
          message += `\n\n${apiError.message}`;
        }
      } else {
        message = apiError.message || 'An error occurred';
      }
      
      // Add suggestions if available
      if (apiError.suggestions && apiError.suggestions.length > 0) {
        message += '\n\nWhat you can do:';
        apiError.suggestions.forEach((suggestion) => {
          message += `\n• ${suggestion}`;
        });
      } else if (apiError.suggestion) {
        // Legacy format
        message += `\n\n💡 ${apiError.suggestion}`;
      }
      
      return new Error(message);
    }

    if (axiosError.code === 'ECONNABORTED') {
      return new Error('Request timed out\n\nThe server took too long to respond. This can happen during high load.\n\nWhat you can do:\n• Wait a moment and try again\n• Check your internet connection');
    }

    if (axiosError.code === 'ERR_NETWORK') {
      return new Error('Cannot connect to server\n\nPlease make sure the backend server is running.\n\nWhat you can do:\n• Check that the backend is running on port 8000\n• Refresh the page and try again');
    }

    return new Error(axiosError.message || 'An unexpected error occurred');
  }

  return error instanceof Error ? error : new Error('An unexpected error occurred');
}

/**
 * Download assignment as markdown file
 */
export function downloadAsMarkdown(assignment: GeneratedAssignment): void {
  const markdown = formatAssignmentAsMarkdown(assignment);
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${assignment.candidate_brief.title.replace(/\s+/g, '_')}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Format assignment as markdown
 */
function formatAssignmentAsMarkdown(assignment: GeneratedAssignment): string {
  const { candidate_brief, evaluator_guide, time_breakdown } = assignment;

  let markdown = `# ${candidate_brief.title}\n\n`;
  markdown += `## Business Context\n\n${candidate_brief.business_context}\n\n`;

  markdown += `## Time Estimate\n\n${candidate_brief.time_estimate}\n\n`;

  markdown += `## Requirements\n\n### Must-Have Features\n\n`;
  candidate_brief.requirements.must_have.forEach((req, i) => {
    markdown += `${i + 1}. **${req.description}** (${req.estimated_time_minutes} min)\n`;
    markdown += `   - Why it matters: ${req.why_it_matters}\n\n`;
  });

  if (candidate_brief.requirements.nice_to_have.length > 0) {
    markdown += `### Nice-to-Have Features\n\n`;
    candidate_brief.requirements.nice_to_have.forEach((req, i) => {
      markdown += `${i + 1}. **${req.description}** (${req.estimated_time_minutes} min)\n`;
      markdown += `   - Why it matters: ${req.why_it_matters}\n\n`;
    });
  }

  if (candidate_brief.requirements.constraints.length > 0) {
    markdown += `### Constraints\n\n`;
    candidate_brief.requirements.constraints.forEach(constraint => {
      markdown += `- ${constraint}\n`;
    });
    markdown += `\n`;
  }

  markdown += `## Submission Guidelines\n\n${candidate_brief.submission_guidelines}\n\n`;

  markdown += `## Evaluation Criteria\n\n`;
  candidate_brief.evaluation_criteria.forEach(criteria => {
    markdown += `- ${criteria}\n`;
  });
  markdown += `\n`;

  markdown += `---\n\n## For Evaluators\n\n`;
  markdown += `### Scoring Rubric\n\n`;
  evaluator_guide.scoring_rubric.forEach(item => {
    markdown += `#### ${item.area} (Weight: ${(item.weight * 100).toFixed(0)}%)\n\n`;
    markdown += `- **Junior**: ${item.junior_expectation}\n`;
    markdown += `- **Mid**: ${item.mid_expectation}\n`;
    markdown += `- **Senior**: ${item.senior_expectation}\n\n`;
    markdown += `**Scoring Guide**: ${item.scoring_guide}\n\n`;
  });

  markdown += `### Common Pitfalls\n\n`;
  evaluator_guide.common_pitfalls.forEach(pitfall => {
    markdown += `- ${pitfall}\n`;
  });
  markdown += `\n`;

  markdown += `### Red Flags 🚩\n\n`;
  evaluator_guide.red_flags.forEach(flag => {
    markdown += `- ${flag}\n`;
  });
  markdown += `\n`;

  markdown += `### Green Flags ✅\n\n`;
  evaluator_guide.green_flags.forEach(flag => {
    markdown += `- ${flag}\n`;
  });
  markdown += `\n`;

  markdown += `### Time Breakdown\n\n`;
  markdown += `- **Total**: ${time_breakdown.total_minutes} minutes\n`;
  markdown += `- Setup: ${time_breakdown.setup_minutes} min\n`;
  markdown += `- Implementation: ${time_breakdown.core_implementation_minutes} min\n`;
  markdown += `- Testing: ${time_breakdown.testing_minutes} min\n`;
  markdown += `- Documentation: ${time_breakdown.documentation_minutes} min\n`;
  markdown += `- Buffer: ${time_breakdown.buffer_minutes} min\n\n`;

  markdown += `---\n\n`;
  markdown += `*Generated on ${new Date(assignment.generated_at).toLocaleString()}*\n`;
  markdown += `*Assignment ID: ${assignment.assignment_id}*\n`;
  markdown += `*Difficulty: ${assignment.estimated_difficulty}*\n`;

  return markdown;
}
