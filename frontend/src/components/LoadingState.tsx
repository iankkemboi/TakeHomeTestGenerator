/**
 * Loading state component with progress indicator
 */

import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

const phases = [
  { label: 'Analyzing job description', time: '10-15s' },
  { label: 'Defining scope & requirements', time: '15-20s' },
  { label: 'Validating assignment', time: '10s' },
  { label: 'Generating rubric', time: '15-20s' },
];

export default function LoadingState({ message = 'Generating assignment...' }: LoadingStateProps) {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <Loader2 className="w-5 h-5 animate-spin" style={{ color: 'var(--accent)' }} />
        <div>
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{message}</p>
          <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>This typically takes 60-90 seconds</p>
        </div>
      </div>

      {/* Phase list - Linear style */}
      <div className="space-y-1">
        {phases.map((phase, i) => (
          <div 
            key={i} 
            className="flex items-center justify-between py-2 px-3 rounded"
            style={{ backgroundColor: i === 0 ? 'var(--accent-muted)' : 'transparent' }}
          >
            <div className="flex items-center space-x-3">
              <div 
                className="w-1.5 h-1.5 rounded-full animate-pulse"
                style={{ 
                  backgroundColor: i === 0 ? 'var(--accent)' : 'var(--text-tertiary)',
                  animationDelay: `${i * 0.2}s`
                }}
              />
              <span 
                className="text-sm"
                style={{ color: i === 0 ? 'var(--text-primary)' : 'var(--text-secondary)' }}
              >
                {phase.label}
              </span>
            </div>
            <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{phase.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
