/**
 * Demo data for simulating API responses without a backend
 */

import type { GeneratedAssignment, AssignmentInput } from '../types/assignment';

/**
 * Generate a realistic demo assignment based on input
 */
export function generateDemoAssignment(input: AssignmentInput): GeneratedAssignment {
  const totalMinutes = Math.round(input.time_budget_hours * 60);
  const setupMinutes = Math.round(totalMinutes * 0.12);
  const implementationMinutes = Math.round(totalMinutes * 0.45);
  const testingMinutes = Math.round(totalMinutes * 0.18);
  const documentationMinutes = Math.round(totalMinutes * 0.10);
  const bufferMinutes = totalMinutes - setupMinutes - implementationMinutes - testingMinutes - documentationMinutes;

  // Generate title based on job title and tech stack
  const title = generateTitle(input);
  
  // Generate business context based on input
  const businessContext = generateBusinessContext(input);
  
  // Generate requirements based on seniority and time budget
  const mustHave = generateMustHaveRequirements(input);
  const niceToHave = generateNiceToHaveRequirements(input);
  const constraints = generateConstraints(input);

  return {
    candidate_brief: {
      title,
      business_context: businessContext,
      requirements: {
        must_have: mustHave,
        nice_to_have: niceToHave,
        constraints,
      },
      submission_guidelines: generateSubmissionGuidelines(input),
      evaluation_criteria: generateEvaluationCriteria(input),
      time_estimate: `${input.time_budget_hours} hours`,
    },
    evaluator_guide: {
      scoring_rubric: generateScoringRubric(input),
      common_pitfalls: [
        "Focusing on implementation details before understanding the problem domain",
        "Neglecting error handling and edge cases",
        "Over-engineering the solution beyond what's needed for the time budget",
        "Poor separation of concerns mixing business logic with infrastructure",
        "Insufficient or missing documentation of design decisions",
      ],
      red_flags: [
        "No README or explanation of approach and trade-offs",
        "Hardcoded values or credentials in the codebase",
        "No tests or broken tests that don't actually validate behavior",
        "Ignoring the stated constraints or time budget",
        "Copy-pasted code without understanding or attribution",
      ],
      green_flags: [
        "Clear documentation explaining design decisions and trade-offs",
        "Well-structured code with appropriate separation of concerns",
        "Thoughtful error handling with informative messages",
        "Tests that validate behavior, not just implementation",
        "Creative solutions that demonstrate deep understanding of the problem",
      ],
      calibration_notes: generateCalibrationNotes(input),
    },
    time_breakdown: {
      total_minutes: totalMinutes,
      setup_minutes: setupMinutes,
      core_implementation_minutes: implementationMinutes,
      testing_minutes: testingMinutes,
      documentation_minutes: documentationMinutes,
      buffer_minutes: bufferMinutes,
      breakdown_valid: true,
    },
    assignment_id: generateUUID(),
    generated_at: new Date().toISOString(),
    estimated_difficulty: estimateDifficulty(input),
    scope_warnings: [],
  };
}

function generateTitle(input: AssignmentInput): string {
  const techPrimary = input.tech_stack[0] || 'Application';
  const roleKeywords = input.job_title.toLowerCase();
  
  if (roleKeywords.includes('backend') || roleKeywords.includes('api')) {
    return `${techPrimary} API Service Design Challenge`;
  } else if (roleKeywords.includes('frontend') || roleKeywords.includes('ui')) {
    return `Interactive ${techPrimary} Interface Challenge`;
  } else if (roleKeywords.includes('fullstack') || roleKeywords.includes('full stack')) {
    return `Full-Stack ${techPrimary} Application Challenge`;
  } else if (roleKeywords.includes('data') || roleKeywords.includes('analytics')) {
    return `Data Processing & Analytics Challenge`;
  }
  return `${techPrimary} Engineering Challenge`;
}

function generateBusinessContext(input: AssignmentInput): string {
  const company = input.company_context || 'a growing technology company';
  const challenges = input.current_challenges || 'scaling our platform to meet increasing demand';
  
  return `You are joining ${company} as a ${input.job_title}. The team is currently focused on ${challenges}.

Your task is to demonstrate your approach to solving a real-world problem similar to what you'd encounter in this role. We're interested in seeing how you think about the problem, make design decisions, and communicate your reasoning.

This assignment is designed to be completed in approximately ${input.time_budget_hours} hours. We value quality over quantity - it's better to have a well-thought-out partial solution than a rushed complete one. Please document any assumptions you make and explain the trade-offs in your approach.

The technologies you'll work with (${input.tech_stack.join(', ')}) are central to our stack, and we're looking for someone who can apply them thoughtfully to solve business problems.`;
}

function generateMustHaveRequirements(input: AssignmentInput): Array<{description: string; estimated_time_minutes: number; why_it_matters: string}> {
  const baseMinutes = Math.round(input.time_budget_hours * 60 * 0.6);
  const perRequirement = Math.round(baseMinutes / 4);
  
  const requirements = [
    {
      description: `Design and implement a core solution that addresses the primary business need. Consider how your design choices will affect maintainability and extensibility.`,
      estimated_time_minutes: perRequirement + 15,
      why_it_matters: `This tests your ability to translate business requirements into working software while making thoughtful architectural decisions.`,
    },
    {
      description: `Implement appropriate data handling and validation. Think about what data integrity means in this context and how to communicate issues clearly.`,
      estimated_time_minutes: perRequirement,
      why_it_matters: `Real-world systems need robust data handling. This shows how you think about edge cases and user experience.`,
    },
    {
      description: `Add meaningful error handling that helps users and developers understand what went wrong and how to fix it.`,
      estimated_time_minutes: perRequirement - 5,
      why_it_matters: `Good error handling is crucial for debugging and user experience. We want to see how you balance technical detail with usability.`,
    },
    {
      description: `Write tests that validate the behavior of your solution. Focus on testing what matters most given the time constraints.`,
      estimated_time_minutes: perRequirement - 10,
      why_it_matters: `Testing strategy reveals how you think about quality and what you consider important to verify.`,
    },
  ];

  // Adjust based on seniority
  if (input.seniority_level === 'senior' || input.seniority_level === 'staff') {
    requirements.push({
      description: `Document your architectural decisions, including alternatives you considered and why you chose your approach.`,
      estimated_time_minutes: 15,
      why_it_matters: `Senior engineers need to communicate technical decisions clearly to stakeholders and team members.`,
    });
  }

  return requirements;
}

function generateNiceToHaveRequirements(_input: AssignmentInput): Array<{description: string; estimated_time_minutes: number; why_it_matters: string}> {
  return [
    {
      description: `Add a feature that demonstrates your understanding of performance considerations or scalability.`,
      estimated_time_minutes: 20,
      why_it_matters: `Shows awareness of production concerns beyond just making things work.`,
    },
    {
      description: `Implement additional functionality that you think would add value, explaining your reasoning.`,
      estimated_time_minutes: 25,
      why_it_matters: `Demonstrates product thinking and ability to prioritize features.`,
    },
  ];
}

function generateConstraints(input: AssignmentInput): string[] {
  const constraints = [
    `Use ${input.tech_stack.join(' or ')} as your primary technology`,
    `Complete within the ${input.time_budget_hours}-hour time budget`,
    `Include a README explaining your approach, assumptions, and how to run your solution`,
  ];

  if (input.avoid_topics && input.avoid_topics.length > 0) {
    constraints.push(`Focus areas should not include: ${input.avoid_topics.join(', ')}`);
  }

  constraints.push(
    `External libraries are allowed - just explain why you chose them`,
    `Prioritize clarity and maintainability over clever solutions`
  );

  return constraints;
}

function generateSubmissionGuidelines(input: AssignmentInput): string {
  const format = input.submission_format;
  
  if (format === 'github') {
    return `Please submit your solution as a GitHub repository. Include a comprehensive README with:
- Setup instructions (how to install dependencies and run the project)
- Your approach and key design decisions
- Any assumptions you made
- What you would do differently with more time
- How to run any tests you've written`;
  } else if (format === 'zip') {
    return `Please submit your solution as a ZIP file containing all source code and a README with setup instructions, your approach, and any assumptions made.`;
  }
  return `Please submit your solution via CodeSandbox or similar online IDE, with a README explaining your approach.`;
}

function generateEvaluationCriteria(input: AssignmentInput): string[] {
  const criteria = [
    'Problem Understanding & Solution Design',
    'Code Quality & Organization',
    'Error Handling & Edge Cases',
    'Testing Approach',
    'Documentation & Communication',
  ];

  if (input.must_evaluate && input.must_evaluate.length > 0) {
    return [...input.must_evaluate.slice(0, 3), ...criteria.slice(0, 2)];
  }

  return criteria;
}

function generateScoringRubric(_input: AssignmentInput): Array<{
  area: string;
  weight: number;
  junior_expectation: string;
  mid_expectation: string;
  senior_expectation: string;
  scoring_guide: string;
}> {
  return [
    {
      area: 'Solution Design & Architecture',
      weight: 0.25,
      junior_expectation: 'Working solution that meets basic requirements. May have some structural issues but demonstrates understanding of the problem.',
      mid_expectation: 'Well-organized solution with clear separation of concerns. Makes reasonable design decisions and can explain trade-offs.',
      senior_expectation: 'Elegant solution demonstrating deep understanding. Anticipates future needs, explains alternatives considered, and justifies choices.',
      scoring_guide: '1: Does not work or misunderstands problem | 2: Works but poorly organized | 3: Functional with reasonable structure | 4: Well-designed with clear thinking | 5: Exceptional design showing mastery',
    },
    {
      area: 'Code Quality & Readability',
      weight: 0.20,
      junior_expectation: 'Readable code with basic organization. Variable names make sense, functions are reasonably sized.',
      mid_expectation: 'Clean, idiomatic code following language conventions. Good abstractions and naming. Easy to follow and modify.',
      senior_expectation: 'Exemplary code that serves as a model. Perfect balance of simplicity and capability. Self-documenting with strategic comments.',
      scoring_guide: '1: Difficult to read/understand | 2: Functional but messy | 3: Clean and readable | 4: Well-crafted and maintainable | 5: Exceptional quality',
    },
    {
      area: 'Error Handling & Robustness',
      weight: 0.20,
      junior_expectation: 'Handles common error cases. Provides basic error messages that indicate what went wrong.',
      mid_expectation: 'Comprehensive error handling with helpful messages. Validates input appropriately. Fails gracefully.',
      senior_expectation: 'Robust error strategy with clear user feedback. Considers security implications. Handles edge cases thoughtfully.',
      scoring_guide: '1: Crashes on errors | 2: Basic error handling | 3: Good coverage of error cases | 4: Robust and user-friendly | 5: Production-ready error handling',
    },
    {
      area: 'Testing Strategy',
      weight: 0.15,
      junior_expectation: 'Some tests present that verify basic functionality. Tests run and pass.',
      mid_expectation: 'Good test coverage of important paths. Tests are readable and maintainable. Covers happy path and key edge cases.',
      senior_expectation: 'Strategic testing that provides confidence. Tests document behavior. Appropriate use of different test types.',
      scoring_guide: '1: No tests or broken tests | 2: Minimal testing | 3: Adequate test coverage | 4: Strong testing strategy | 5: Comprehensive and well-designed tests',
    },
    {
      area: 'Documentation & Communication',
      weight: 0.20,
      junior_expectation: 'README with setup instructions. Code has some comments where needed.',
      mid_expectation: 'Clear README explaining approach and decisions. Well-documented code. Easy for others to understand and run.',
      senior_expectation: 'Excellent documentation that tells a story. Explains why, not just what. Discusses trade-offs and alternatives.',
      scoring_guide: '1: No documentation | 2: Minimal README | 3: Good documentation | 4: Comprehensive and clear | 5: Exceptional communication',
    },
  ];
}

function generateCalibrationNotes(input: AssignmentInput): string {
  return `When evaluating submissions, remember that this is a ${input.time_budget_hours}-hour assignment for a ${input.seniority_level} ${input.job_title} position.

Focus on evaluating the candidate's thinking and decision-making process, not just the final output. Different valid approaches should score equally well - there's no single "correct" solution. Look for evidence of thoughtful trade-offs and clear communication of reasoning.

Pay attention to how candidates handle uncertainty and constraints. A well-documented partial solution that explains what would come next is often more valuable than a complete but poorly explained one. The README and code comments are as important as the code itself for understanding how the candidate thinks.

Be especially attentive to how candidates from different backgrounds might approach the problem differently. Evaluate the quality of their reasoning, not whether they match a predetermined solution pattern.`;
}

function estimateDifficulty(input: AssignmentInput): 'easy' | 'medium' | 'hard' {
  if (input.seniority_level === 'junior') return 'easy';
  if (input.seniority_level === 'staff') return 'hard';
  if (input.time_budget_hours >= 6) return 'hard';
  if (input.time_budget_hours <= 2) return 'easy';
  return 'medium';
}

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Simulate API delay for realistic demo experience
 */
export function simulateDelay(minMs: number = 2000, maxMs: number = 4000): Promise<void> {
  const delay = Math.random() * (maxMs - minMs) + minMs;
  return new Promise((resolve) => setTimeout(resolve, delay));
}
