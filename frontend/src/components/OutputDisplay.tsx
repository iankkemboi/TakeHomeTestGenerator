/**
 * Output display component with markdown rendering and tabs
 */

import ReactMarkdown from 'react-markdown';
import * as Tabs from '@radix-ui/react-tabs';
import { Download, AlertCircle, CheckCircle2, Clock, RefreshCw } from 'lucide-react';
import type { GeneratedAssignment } from '../types/assignment';
import { downloadAsMarkdown } from '../api/client';

interface OutputDisplayProps {
  assignment: GeneratedAssignment;
  onStartNew: () => void;
  onRetry: () => void;
}

export default function OutputDisplay({ assignment, onStartNew, onRetry }: OutputDisplayProps) {
  const { candidate_brief, evaluator_guide, time_breakdown, estimated_difficulty, scope_warnings } = assignment;

  const difficultyStyles: Record<string, { bg: string; color: string }> = {
    easy: { bg: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' },
    medium: { bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' },
    hard: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' },
  };

  return (
    <div className="space-y-4">
      {/* Header with metadata - Linear style */}
      <div className="linear-card p-5">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-base font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
              {candidate_brief.title}
            </h1>
            <div className="flex items-center space-x-3 text-xs">
              <span 
                className="px-2 py-1 rounded font-medium"
                style={{ backgroundColor: difficultyStyles[estimated_difficulty].bg, color: difficultyStyles[estimated_difficulty].color }}
              >
                {estimated_difficulty.charAt(0).toUpperCase() + estimated_difficulty.slice(1)}
              </span>
              <span className="flex items-center" style={{ color: 'var(--text-tertiary)' }}>
                <Clock className="w-3.5 h-3.5 mr-1" />
                {candidate_brief.time_estimate}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            <button onClick={() => downloadAsMarkdown(assignment)} className="linear-btn-secondary inline-flex items-center text-xs">
              <Download className="w-3.5 h-3.5 mr-1.5" />
              Download
            </button>
            <button onClick={onRetry} className="linear-btn-primary inline-flex items-center text-xs">
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Regenerate
            </button>
            <button onClick={onStartNew} className="linear-btn-secondary text-xs">
              Start new
            </button>
          </div>
        </div>

        {/* Warnings */}
        {scope_warnings.length > 0 && (
          <div className="mt-4 p-3 rounded" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            <div className="flex items-start">
              <AlertCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" style={{ color: '#f59e0b' }} />
              <div>
                <h3 className="text-xs font-medium" style={{ color: '#f59e0b' }}>Scope Warnings</h3>
                <ul className="mt-1 text-xs space-y-0.5" style={{ color: 'var(--text-secondary)' }}>
                  {scope_warnings.map((warning, i) => (
                    <li key={i}>• {warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tabbed content - Linear style */}
      <Tabs.Root defaultValue="candidate" className="linear-card overflow-hidden">
        <Tabs.List className="flex" style={{ borderBottom: '1px solid var(--border-primary)' }}>
          <Tabs.Trigger
            value="candidate"
            className="px-4 py-3 text-xs font-medium transition-colors data-[state=active]:border-b-2"
            style={{ color: 'var(--text-secondary)' }}
          >
            Candidate Brief
          </Tabs.Trigger>
          <Tabs.Trigger
            value="evaluator"
            className="px-4 py-3 text-xs font-medium transition-colors data-[state=active]:border-b-2"
            style={{ color: 'var(--text-secondary)' }}
          >
            Evaluator Guide
          </Tabs.Trigger>
          <Tabs.Trigger
            value="breakdown"
            className="px-4 py-3 text-xs font-medium transition-colors data-[state=active]:border-b-2"
            style={{ color: 'var(--text-secondary)' }}
          >
            Time Breakdown
          </Tabs.Trigger>
        </Tabs.List>

        {/* Candidate Brief Tab */}
        <Tabs.Content value="candidate" className="p-5">
          <div className="space-y-6">
            <div>
              <h2 className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Business Context</h2>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{candidate_brief.business_context}</p>
            </div>

            <div>
              <h2 className="text-sm font-medium mb-3" style={{ color: 'var(--text-primary)' }}>Requirements</h2>
              <h3 className="text-xs font-medium mb-2" style={{ color: '#22c55e' }}>Must-Have Features</h3>
              <div className="space-y-2">
                {candidate_brief.requirements.must_have.map((req, i) => (
                  <div key={i} className="p-3 rounded" style={{ backgroundColor: 'var(--bg-tertiary)', borderLeft: '2px solid #22c55e' }}>
                    <div className="flex items-start justify-between">
                      <h4 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{req.description}</h4>
                      <span className="text-xs whitespace-nowrap ml-3 font-mono" style={{ color: '#22c55e' }}>
                        {req.estimated_time_minutes}m
                      </span>
                    </div>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                      {req.why_it_matters}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {candidate_brief.requirements.nice_to_have.length > 0 && (
              <div>
                <h3 className="text-xs font-medium mb-2" style={{ color: 'var(--accent)' }}>Nice-to-Have Features</h3>
                <div className="space-y-2">
                  {candidate_brief.requirements.nice_to_have.map((req, i) => (
                    <div key={i} className="p-3 rounded" style={{ backgroundColor: 'var(--bg-tertiary)', borderLeft: '2px solid var(--accent)' }}>
                      <div className="flex items-start justify-between">
                        <h4 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{req.description}</h4>
                        <span className="text-xs whitespace-nowrap ml-3 font-mono" style={{ color: 'var(--accent)' }}>
                          {req.estimated_time_minutes}m
                        </span>
                      </div>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                        {req.why_it_matters}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {candidate_brief.requirements.constraints.length > 0 && (
              <div>
                <h3 className="text-xs font-medium mb-2" style={{ color: '#f59e0b' }}>Constraints</h3>
                <ul className="space-y-1">
                  {candidate_brief.requirements.constraints.map((constraint, i) => (
                    <li key={i} className="text-sm flex items-start" style={{ color: 'var(--text-secondary)' }}>
                      <span className="mr-2" style={{ color: '#f59e0b' }}>•</span>
                      {constraint}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              <h2 className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Submission Guidelines</h2>
              <div className="prose-linear">
                <ReactMarkdown>{candidate_brief.submission_guidelines}</ReactMarkdown>
              </div>
            </div>

            <div>
              <h2 className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Evaluation Criteria</h2>
              <ul className="space-y-1">
                {candidate_brief.evaluation_criteria.map((criteria, i) => (
                  <li key={i} className="text-sm flex items-start" style={{ color: 'var(--text-secondary)' }}>
                    <span className="mr-2" style={{ color: 'var(--accent)' }}>✓</span>
                    {criteria}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Tabs.Content>

        {/* Evaluator Guide Tab */}
        <Tabs.Content value="evaluator" className="p-5">
          <div className="space-y-6">
            <div>
              <h2 className="text-sm font-medium mb-3" style={{ color: 'var(--text-primary)' }}>Scoring Rubric</h2>
              <div className="space-y-3">
                {evaluator_guide.scoring_rubric.map((item, i) => (
                  <div key={i} className="p-4 rounded" style={{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-primary)' }}>
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{item.area}</h3>
                      <span className="text-xs font-medium px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--accent-muted)', color: 'var(--accent)' }}>
                        {(item.weight * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div className="p-2 rounded" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                        <p className="font-medium mb-1" style={{ color: 'var(--text-tertiary)' }}>Junior</p>
                        <p style={{ color: 'var(--text-secondary)' }}>{item.junior_expectation}</p>
                      </div>
                      <div className="p-2 rounded" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                        <p className="font-medium mb-1" style={{ color: 'var(--text-tertiary)' }}>Mid-Level</p>
                        <p style={{ color: 'var(--text-secondary)' }}>{item.mid_expectation}</p>
                      </div>
                      <div className="p-2 rounded" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                        <p className="font-medium mb-1" style={{ color: 'var(--text-tertiary)' }}>Senior</p>
                        <p style={{ color: 'var(--text-secondary)' }}>{item.senior_expectation}</p>
                      </div>
                    </div>
                    <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--border-primary)' }}>
                      <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                        {item.scoring_guide}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded" style={{ backgroundColor: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.15)' }}>
                <h3 className="text-xs font-medium mb-2" style={{ color: '#f59e0b' }}>Common Pitfalls</h3>
                <ul className="space-y-1">
                  {evaluator_guide.common_pitfalls.map((pitfall, i) => (
                    <li key={i} className="text-xs flex items-start" style={{ color: 'var(--text-secondary)' }}>
                      <span className="mr-1.5" style={{ color: '#f59e0b' }}>⚠</span>
                      {pitfall}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded" style={{ backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.15)' }}>
                <h3 className="text-xs font-medium mb-2" style={{ color: '#ef4444' }}>Red Flags</h3>
                <ul className="space-y-1">
                  {evaluator_guide.red_flags.map((flag, i) => (
                    <li key={i} className="text-xs flex items-start" style={{ color: 'var(--text-secondary)' }}>
                      <span className="mr-1.5" style={{ color: '#ef4444' }}>•</span>
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="p-4 rounded" style={{ backgroundColor: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.15)' }}>
              <h3 className="text-xs font-medium mb-2 flex items-center" style={{ color: '#22c55e' }}>
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Green Flags
              </h3>
              <ul className="space-y-1">
                {evaluator_guide.green_flags.map((flag, i) => (
                  <li key={i} className="text-xs flex items-start" style={{ color: 'var(--text-secondary)' }}>
                    <span className="mr-1.5" style={{ color: '#22c55e' }}>✓</span>
                    {flag}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded" style={{ backgroundColor: 'var(--accent-muted)', border: '1px solid rgba(94, 106, 210, 0.2)' }}>
              <h3 className="text-xs font-medium mb-2" style={{ color: 'var(--accent)' }}>Calibration Notes</h3>
              <p className="text-xs whitespace-pre-line leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {evaluator_guide.calibration_notes}
              </p>
            </div>
          </div>
        </Tabs.Content>

        {/* Time Breakdown Tab */}
        <Tabs.Content value="breakdown" className="p-5">
          <div className="max-w-lg">
            <h2 className="text-sm font-medium mb-4" style={{ color: 'var(--text-primary)' }}>Time Breakdown</h2>
            <div className="space-y-3">
              <TimeBreakdownBar label="Setup" minutes={time_breakdown.setup_minutes} total={time_breakdown.total_minutes} color="#a855f7" />
              <TimeBreakdownBar label="Implementation" minutes={time_breakdown.core_implementation_minutes} total={time_breakdown.total_minutes} color="var(--accent)" />
              <TimeBreakdownBar label="Testing" minutes={time_breakdown.testing_minutes} total={time_breakdown.total_minutes} color="#22c55e" />
              <TimeBreakdownBar label="Documentation" minutes={time_breakdown.documentation_minutes} total={time_breakdown.total_minutes} color="#f59e0b" />
              <TimeBreakdownBar label="Buffer" minutes={time_breakdown.buffer_minutes} total={time_breakdown.total_minutes} color="#71717a" />
            </div>
            <div className="mt-5 pt-4" style={{ borderTop: '1px solid var(--border-primary)' }}>
              <div className="flex items-center justify-between text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                <span>Total</span>
                <span className="font-mono">{time_breakdown.total_minutes}m <span style={{ color: 'var(--text-tertiary)' }}>({(time_breakdown.total_minutes / 60).toFixed(1)}h)</span></span>
              </div>
              {time_breakdown.breakdown_valid ? (
                <p className="text-xs mt-2 flex items-center" style={{ color: '#22c55e' }}>
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                  Valid breakdown
                </p>
              ) : (
                <p className="text-xs mt-2 flex items-center" style={{ color: '#f59e0b' }}>
                  <AlertCircle className="w-3.5 h-3.5 mr-1.5" />
                  Components don't sum exactly to total
                </p>
              )}
            </div>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}

interface TimeBreakdownBarProps {
  label: string;
  minutes: number;
  total: number;
  color: string;
}

function TimeBreakdownBar({ label, minutes, total, color }: TimeBreakdownBarProps) {
  const percentage = (minutes / total) * 100;

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{minutes}m ({percentage.toFixed(0)}%)</span>
      </div>
      <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
        <div
          className="h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
