/**
 * Multi-step input form for assignment generation
 */

import { useState } from 'react';
import type { AssignmentInput, SeniorityLevel, SubmissionFormat } from '../types/assignment';
import { ChevronRight, ChevronLeft } from 'lucide-react';

interface InputFormProps {
  onSubmit: (input: AssignmentInput) => void;
  isLoading: boolean;
}

export default function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<AssignmentInput>({
    job_title: '',
    job_description: '',
    tech_stack: [],
    time_budget_hours: 4.0,
    seniority_level: 'mid' as SeniorityLevel,
    company_context: '',
    current_challenges: '',
    must_evaluate: [],
    avoid_topics: [],
    candidate_can_use: [],
    submission_format: 'github' as SubmissionFormat,
  });

  const [techStackInput, setTechStackInput] = useState('');
  const [mustEvaluateInput, setMustEvaluateInput] = useState('');
  const [avoidTopicsInput, setAvoidTopicsInput] = useState('');

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addTag = (field: 'tech_stack' | 'must_evaluate' | 'avoid_topics', value: string) => {
    if (value.trim()) {
      setFormData({
        ...formData,
        [field]: [...formData[field], value.trim()]
      });
    }
  };

  const removeTag = (field: 'tech_stack' | 'must_evaluate' | 'avoid_topics', index: number) => {
    setFormData({
      ...formData,
      [field]: formData[field].filter((_, i) => i !== index)
    });
  };

  const canProceedStep1 = formData.job_title && formData.job_description.length >= 100 && formData.tech_stack.length > 0;
  const canProceedStep2 = formData.time_budget_hours >= 2 && formData.time_budget_hours <= 8;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Progress indicator - Linear style: minimal dots */}
      <div className="flex items-center justify-between mb-6 pb-4" style={{ borderBottom: '1px solid var(--border-primary)' }}>
        <div className="flex items-center space-x-1">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className="w-6 h-6 rounded flex items-center justify-center text-xs font-medium transition-all"
                style={{
                  backgroundColor: s === step ? 'var(--accent)' : s < step ? 'var(--accent-muted)' : 'var(--bg-tertiary)',
                  color: s === step ? 'white' : s < step ? 'var(--accent)' : 'var(--text-tertiary)',
                }}
              >
                {s < step ? '✓' : s}
              </div>
              {s < 3 && (
                <div className="w-8 h-px mx-1" style={{ backgroundColor: s < step ? 'var(--accent)' : 'var(--border-primary)' }} />
              )}
            </div>
          ))}
        </div>
        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Step {step} of 3</span>
      </div>

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>Job Details</h2>
            <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Enter the position information</p>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Job Title
            </label>
            <input
              type="text"
              value={formData.job_title}
              onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
              className="linear-input w-full"
              placeholder="e.g., Senior Backend Engineer"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Job Description <span style={{ color: 'var(--text-tertiary)' }}>(min 100 characters)</span>
            </label>
            <textarea
              value={formData.job_description}
              onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
              rows={6}
              className="linear-input w-full resize-none"
              placeholder="Describe the role, responsibilities, tech stack, and requirements..."
              required
              minLength={100}
            />
            <p className="text-xs mt-1.5" style={{ color: 'var(--text-tertiary)' }}>
              <span style={{ color: formData.job_description.length >= 100 ? '#22c55e' : 'var(--text-tertiary)' }}>{formData.job_description.length}</span> / 100
            </p>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Tech Stack <span style={{ color: 'var(--text-tertiary)' }}>(press Enter to add)</span>
            </label>
            <input
              type="text"
              value={techStackInput}
              onChange={(e) => setTechStackInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addTag('tech_stack', techStackInput);
                  setTechStackInput('');
                }
              }}
              className="linear-input w-full"
              placeholder="e.g., Python, FastAPI, PostgreSQL"
            />
            <div className="flex flex-wrap gap-1.5 mt-2">
              {formData.tech_stack.map((tech, i) => (
                <span key={i} className="linear-tag">
                  {tech}
                  <button
                    type="button"
                    onClick={() => removeTag('tech_stack', i)}
                    className="ml-1.5 hover:text-white transition-colors"
                    style={{ color: 'var(--text-tertiary)' }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Assignment Details */}
      {step === 2 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>Assignment Details</h2>
            <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Configure the assignment parameters</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                Time Budget (hours)
              </label>
              <input
                type="number"
                value={formData.time_budget_hours}
                onChange={(e) => setFormData({ ...formData, time_budget_hours: parseFloat(e.target.value) })}
                min={2}
                max={8}
                step={0.5}
                className="linear-input w-full"
                required
              />
              <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>2-8 hours</p>
            </div>

            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                Seniority Level
              </label>
              <select
                value={formData.seniority_level}
                onChange={(e) => setFormData({ ...formData, seniority_level: e.target.value as SeniorityLevel })}
                className="linear-input w-full cursor-pointer"
                required
              >
                <option value="junior">Junior</option>
                <option value="mid">Mid-Level</option>
                <option value="senior">Senior</option>
                <option value="staff">Staff</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Must Evaluate <span style={{ color: 'var(--text-tertiary)' }}>(press Enter)</span>
            </label>
            <input
              type="text"
              value={mustEvaluateInput}
              onChange={(e) => setMustEvaluateInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addTag('must_evaluate', mustEvaluateInput);
                  setMustEvaluateInput('');
                }
              }}
              className="linear-input w-full"
              placeholder="e.g., API design, error handling"
            />
            <div className="flex flex-wrap gap-1.5 mt-2">
              {formData.must_evaluate.map((skill, i) => (
                <span key={i} className="linear-tag" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)', borderColor: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' }}>
                  {skill}
                  <button type="button" onClick={() => removeTag('must_evaluate', i)} className="ml-1.5 hover:text-white">×</button>
                </span>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Avoid Topics <span style={{ color: 'var(--text-tertiary)' }}>(press Enter)</span>
            </label>
            <input
              type="text"
              value={avoidTopicsInput}
              onChange={(e) => setAvoidTopicsInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addTag('avoid_topics', avoidTopicsInput);
                  setAvoidTopicsInput('');
                }
              }}
              className="linear-input w-full"
              placeholder="e.g., algorithms, system design"
            />
            <div className="flex flex-wrap gap-1.5 mt-2">
              {formData.avoid_topics.map((topic, i) => (
                <span key={i} className="linear-tag" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' }}>
                  {topic}
                  <button type="button" onClick={() => removeTag('avoid_topics', i)} className="ml-1.5 hover:text-white">×</button>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Optional Details */}
      {step === 3 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>Additional Context</h2>
            <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Optional information to improve results</p>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Company Context
            </label>
            <textarea
              value={formData.company_context}
              onChange={(e) => setFormData({ ...formData, company_context: e.target.value })}
              rows={3}
              className="linear-input w-full resize-none"
              placeholder="Company description, product domain, team size..."
            />
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Current Challenges
            </label>
            <textarea
              value={formData.current_challenges}
              onChange={(e) => setFormData({ ...formData, current_challenges: e.target.value })}
              rows={3}
              className="linear-input w-full resize-none"
              placeholder="Team pain points, scaling issues, technical debt..."
            />
          </div>

          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Submission Format
            </label>
            <select
              value={formData.submission_format}
              onChange={(e) => setFormData({ ...formData, submission_format: e.target.value as SubmissionFormat })}
              className="linear-input w-full cursor-pointer"
            >
              <option value="github">GitHub Repository</option>
              <option value="zip">ZIP File</option>
              <option value="codesandbox">CodeSandbox</option>
            </select>
          </div>
        </div>
      )}

      {/* Navigation buttons - Linear style */}
      <div className="flex justify-between pt-5 mt-6" style={{ borderTop: '1px solid var(--border-primary)' }}>
        <button
          type="button"
          onClick={handlePrev}
          disabled={step === 1}
          className="linear-btn-secondary inline-flex items-center disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-3.5 h-3.5 mr-1" />
          Previous
        </button>

        {step < 3 ? (
          <button
            type="button"
            onClick={handleNext}
            disabled={(step === 1 && !canProceedStep1) || (step === 2 && !canProceedStep2)}
            className="linear-btn-primary inline-flex items-center disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Continue
            <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={isLoading}
            className="linear-btn-primary inline-flex items-center disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Generating...' : 'Generate assignment'}
          </button>
        )}
      </div>
    </form>
  );
}
