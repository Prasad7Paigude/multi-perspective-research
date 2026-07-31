import { useState, useEffect, useRef } from 'react';
import { Users, MessageCircle, FileText, CheckCircle2, Loader2, Brain } from 'lucide-react';
import type { ThinkingState } from '../types';

interface ResearchProgressProps {
  sections: string[];
  isComplete: boolean;
  thinkingState?: ThinkingState | null;
}

const steps = [
  { id: 'analysts', label: 'Analyst Panel', icon: Users },
  { id: 'interviews', label: 'Expert Interviews', icon: MessageCircle },
  { id: 'report', label: 'Report Synthesis', icon: FileText },
];

function ResearchProgress({ sections, isComplete, thinkingState }: ResearchProgressProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [displayedContent, setDisplayedContent] = useState('');
  const contentRef = useRef<HTMLDivElement>(null);

  // Animate thinking content for ChatGPT-like streaming effect
  useEffect(() => {
    if (thinkingState && thinkingState.content && !thinkingState.isComplete) {
      // Scroll to bottom when new content arrives
      const timer = setTimeout(() => {
        contentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [thinkingState?.content]);

  // Update displayed content when thinking state changes
  useEffect(() => {
    if (thinkingState?.content) {
      setDisplayedContent(thinkingState.content);
    } else {
      setDisplayedContent('');
    }
  }, [thinkingState?.content]);

  useEffect(() => {
    if (sections.length > 0) {
      setCurrentStep(2); // Interviews complete, report synthesis in progress
    }
    if (isComplete) {
      setCurrentStep(3); // Complete
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

      {/* Thinking Display - ChatGPT-like streaming */}
      {thinkingState && (
        <div className="bg-bg-secondary rounded-xl border border-accent/30 p-5 mb-6 animate-fadeIn">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
              <Brain className="w-4 h-4 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium text-accent">
                  {thinkingState.analystName}
                </span>
                <span className="text-xs text-text-tertiary">
                  {thinkingState.analystRole}
                </span>
              </div>
              <div className="text-sm text-text-primary leading-relaxed">
                <span ref={contentRef}>{displayedContent}</span>
                {!thinkingState.isComplete && (
                  <span className="inline-flex gap-0.5 ml-1">
                    <span className="w-1 h-4 bg-accent rounded-sm animate-think-blink" />
                    <span className="w-1 h-4 bg-accent rounded-sm animate-think-blink" style={{ animationDelay: '0.2s' }} />
                    <span className="w-1 h-4 bg-accent rounded-sm animate-think-blink" style={{ animationDelay: '0.4s' }} />
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

export default ResearchProgress;