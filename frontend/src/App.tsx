/**
 * Main App component
 */

import { useState } from 'react';
import InputForm from './components/InputForm';
import OutputDisplay from './components/OutputDisplay';
import LoadingState from './components/LoadingState';
import { generateAssignment, isDemoMode } from './api/client';
import type { AssignmentInput, GeneratedAssignment } from './types/assignment';
import { RefreshCw, AlertCircle, FlaskConical } from 'lucide-react';

type AppState = 'input' | 'loading' | 'output' | 'error';

function App() {
  const [state, setState] = useState<AppState>('input');
  const [assignment, setAssignment] = useState<GeneratedAssignment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastInput, setLastInput] = useState<AssignmentInput | null>(null);

  const handleGenerate = async (input: AssignmentInput) => {
    setState('loading');
    setError(null);
    setLastInput(input);

    try {
      const result = await generateAssignment(input);
      setAssignment(result);
      setState('output');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setState('error');
    }
  };

  const handleStartNew = () => {
    setState('input');
    setAssignment(null);
    setError(null);
    setLastInput(null);
  };

  const handleRetry = () => {
    if (lastInput) {
      handleGenerate(lastInput);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header - Linear style: minimal, left-aligned */}
      <header className="border-b" style={{ borderColor: 'var(--border-primary)', backgroundColor: 'var(--bg-secondary)' }}>
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--accent)' }}>
                <span className="text-white font-semibold text-sm">TH</span>
              </div>
              <div>
                <h1 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Take-Home Test Generator
                </h1>
                <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                  AI-powered coding assignments
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {isDemoMode() && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs" style={{ backgroundColor: 'rgba(251, 191, 36, 0.15)', color: '#f59e0b' }}>
                  <FlaskConical className="w-3 h-3 mr-1" />
                  Demo Mode
                </span>
              )}
              <span className="inline-flex items-center px-2 py-1 rounded text-xs" style={{ backgroundColor: 'var(--accent-muted)', color: 'var(--accent)' }}>
                <span className="w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: isDemoMode() ? '#f59e0b' : '#22c55e' }}></span>
                {isDemoMode() ? 'Simulated' : 'Gemini AI'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-8">
        {state === 'input' && (
          <div className="linear-card p-6">
            <InputForm onSubmit={handleGenerate} isLoading={false} />
          </div>
        )}

        {state === 'loading' && (
          <div className="linear-card">
            <LoadingState />
          </div>
        )}

        {state === 'output' && assignment && (
          <OutputDisplay 
            assignment={assignment} 
            onStartNew={handleStartNew}
            onRetry={handleRetry}
          />
        )}

        {state === 'error' && (
          <div className="linear-card p-6">
            <div className="flex items-start space-x-3">
              <div className="p-2 rounded-md" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }}>
                <AlertCircle className="w-5 h-5" style={{ color: '#ef4444' }} />
              </div>
              <div className="flex-1">
                <h2 className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Generation failed
                </h2>
                <p className="text-sm whitespace-pre-line mb-4" style={{ color: 'var(--text-secondary)' }}>{error}</p>
                <div className="flex space-x-2">
                  <button onClick={handleRetry} className="linear-btn-primary inline-flex items-center">
                    <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                    Try again
                  </button>
                  <button onClick={handleStartNew} className="linear-btn-secondary">
                    Start new
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer - Linear style: minimal */}
      <footer className="border-t py-4" style={{ borderColor: 'var(--border-primary)' }}>
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            {isDemoMode() 
              ? 'Demo mode: Simulated responses (no backend required)' 
              : 'Generation time: ~60-90 seconds'}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
