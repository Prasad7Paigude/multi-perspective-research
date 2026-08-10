import { useState, useEffect } from 'react';
import { Users, MessageCircle, FileText, CheckCircle2, Loader2, Brain } from 'lucide-react';

interface ResearchProgressProps {
  sections: string[];
  isComplete: boolean;
  interviewProgress?: {
    current: number;
    total: number;
    percentage: number;
    etaSeconds: number | null;
    currentAnalyst: string | null;
    currentTurn: number;
    totalAnalysts: number;
    isStale: boolean;
  };
}

function ResearchProgress({ sections, isComplete, interviewProgress }: ResearchProgressProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [eta, setEta] = useState('Estimating time remaining...');
  const [statusLine, setStatusLine] = useState('Starting parallel interviews...');
  const [isStale, setIsStale] = useState(false);

  // Calculate progress and ETA from interviewProgress
  useEffect(() => {
    if (interviewProgress) {
      const p = interviewProgress.percentage || 0;
      setProgress(Math.min(100, Math.round(p)));
      setIsStale(interviewProgress.isStale || false);

      // Format ETA
      if (interviewProgress.etaSeconds !== null && interviewProgress.etaSeconds !== undefined) {
        const etaSeconds = interviewProgress.etaSeconds;
        if (etaSeconds < 60) {
          setEta(`~${Math.round(etaSeconds)} seconds`);
        } else {
          setEta(`~${Math.round(etaSeconds / 60)} min`);
        }
      } else {
        setEta('Estimating time remaining...');
      }

      // Format status line
      if (interviewProgress.currentAnalyst) {
        const turnsPerAnalyst = interviewProgress.total / interviewProgress.totalAnalysts || 1;
        setStatusLine(
          `${interviewProgress.currentAnalyst} — Turn ${interviewProgress.currentTurn} of ${Math.round(turnsPerAnalyst)}`
        );
      } else {
        setStatusLine('Starting parallel interviews...');
      }
    }
  }, [interviewProgress]);

  useEffect(() => {
    if (sections.length > 0) {
      setCurrentStep(2);
    }
    if (isComplete) {
      setCurrentStep(3);
    }
  }, [sections.length, isComplete]);

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-accent animate-spin" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            Research in Progress
          </h2>
          <p className="text-sm text-text-secondary">
            Our AI analysts are conducting interviews and synthesizing findings.
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      {interviewProgress && (
        <div className="mb-6">
          <div className="flex justify-between text-xs mb-1 text-text-primary">
            <span>Overall Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-accent transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="text-xs text-text-secondary mt-1">{eta} remaining</div>
        </div>
      )}

      {/* Step Indicator */}
      <div className="bg-bg-secondary rounded-xl border border-border-primary p-6 mb-6">
        <div className="flex items-center justify-between">
          {steps.map((step, i) => (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                    i < currentStep
                      ? 'bg-success text-white'
                      : i === currentStep
                      ? 'bg-accent text-white ring-4 ring-accent/20'
                      : 'bg-bg-tertiary text-text-tertiary'
                  }`}
                >
                  {i < currentStep ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <step.icon className="w-5 h-5" />
                  )}
                </div>
                <span
                  className={`text-xs font-medium mt-2 ${
                    i <= currentStep ? 'text-text-primary' : 'text-text-tertiary'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 mt-[-1.5rem] transition-colors duration-500 ${
                    i < currentStep ? 'bg-success' : 'bg-bg-tertiary'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Real-Time Progress Indicator */}
      {interviewProgress && (
        <div className="bg-bg-secondary rounded-xl border border-accent/30 p-5 mb-6 animate-fadeIn">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
              <Brain className="w-4 h-4 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium text-accent">
                  {interviewProgress.currentAnalyst || 'Analyst'}
                </span>
                <span className="text-xs text-text-tertiary">
                  {statusLine}
                </span>
              </div>
              <div className="text-sm text-text-primary leading-relaxed">
                {eta}
                {isStale && (
                  <span className="ml-2 text-xs text-warning">
                    (Connection lost — showing last known progress)
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Log */}
      <div className="bg-bg-secondary rounded-xl border border-border-primary p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
            <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
            <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
          </div>
          <span className="text-xs font-medium text-text-secondary">
            Live Activity
          </span>
        <div className="text-xs text-text-tertiary mb-4">
          {statusLine}
        </div>
        </div>

        <div className="space-y-3 max-h-80 overflow-y-auto">
          {/* Status messages */}
          {currentStep === 0 && (
            <div className="flex items-center gap-2 text-xs text-text-tertiary animate-fadeIn">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              Initializing analyst panel...
            </div>
          )}
          {currentStep >= 1 && (
            <div className="flex items-center gap-2 text-xs text-success animate-fadeIn">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Analyst panel assembled and approved
            </div>
          )}
          {sections.map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-2 text-xs text-text-secondary animate-fadeIn"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-success shrink-0" />
              Interview {i + 1} completed — section written
            </div>
          ))}
          {currentStep === 1 && sections.length > 0 && (
            <div className="flex items-center gap-2 text-xs text-text-tertiary animate-fadeIn">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              Synthesizing final report...
            </div>
          )}
          {isComplete && (
            <div className="flex items-center gap-2 text-xs text-success font-medium animate-fadeIn">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Research complete — report ready
            </div>
          )}
        </div>
      </div>

      {/* Section previews */}
      {sections.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider">
            Completed Sections
          </h3>
          {sections.map((section, i) => (
            <div
              key={i}
              className="bg-bg-secondary rounded-xl border border-border-primary p-4 animate-slideUp"
              style={{ animationDelay: `${i * 0.15}s` }}
            >
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                <span className="text-xs font-medium text-text-primary">
                  Section {i + 1}
                </span>
              </div>
              <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed">
                {section.replace(/^##\s+/, '').split('\n')[0]}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const steps = [
  { id: 'analysts', label: 'Analyst Panel', icon: Users },
  { id: 'interviews', label: 'Expert Interviews', icon: MessageCircle },
  { id: 'report', label: 'Report Synthesis', icon: FileText },
];

export default ResearchProgress;
