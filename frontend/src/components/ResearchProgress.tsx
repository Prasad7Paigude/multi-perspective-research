import { useState, useEffect, useRef, useMemo } from 'react';
import { Users, MessageCircle, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import SimulatedProgressBar from './SimulatedProgressBar';

interface ResearchProgressProps {
  sections: string[];
  isComplete: boolean;
}

const steps = [
  { id: 'analysts', label: 'Analyst Panel', icon: Users },
  { id: 'interviews', label: 'Expert Interviews', icon: MessageCircle },
  { id: 'report', label: 'Report Synthesis', icon: FileText },
];

function ResearchProgress({ sections, isComplete }: ResearchProgressProps) {
  const progressBarRef = useRef<any>(null);

  // Randomized stage thresholds - generated once per run for natural pacing
  const stageThresholdsRef = useRef<{ stage1: number; stage2: number } | null>(null);
  if (!stageThresholdsRef.current) {
    stageThresholdsRef.current = {
      stage1: 25 + Math.random() * 15, // 25-40% for stage 1 transition
      stage2: 55 + Math.random() * 20, // 55-75% for stage 2 transition
    };
  }

  // Track the simulated progress value from the progress bar
  const [progressValue, setProgressValue] = useState(0);

  // Compute the current step from progress, randomized thresholds, and real completion
  const currentStep = useMemo(() => {
    if (isComplete) return 3;
    const { stage1, stage2 } = stageThresholdsRef.current!;
    if (progressValue < stage1) return 0;
    if (progressValue < stage2) return 1;
    return 2;
  }, [progressValue, isComplete]);

  useEffect(() => {
    if (isComplete) {
      // Trigger progress bar to animate to 100%
      if (progressBarRef.current) {
        progressBarRef.current.complete();
      }
    }
  }, [isComplete]);

  return (
    <div className="animate-fadeIn">
      <div className="flex items-center gap-3.5 mb-8">
        <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center gemini-card shrink-0">
          <Loader2 className="w-5 h-5 text-[#4285f4] animate-spin" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-text-primary tracking-tight">Research in Progress</h2>
          <p className="text-sm text-text-secondary leading-relaxed">
            Our AI analysts are conducting interviews and synthesizing findings.
          </p>
        </div>
      </div>

      <div className="mb-6">
        <SimulatedProgressBar 
          ref={progressBarRef} 
          onProgress={setProgressValue}
          onComplete={() => {
            // currentStep is driven by isComplete prop via useMemo
          }}
        />
      </div>

      <div className="gemini-card p-6 mb-6">
        <div className="flex items-center justify-between">
          {steps.map((step, i) => (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 shadow-sm ${
                    i < currentStep
                      ? 'bg-success text-white'
                      : i === currentStep
                      ? 'bg-gradient-to-tr from-[#4285f4] to-[#9b51e0] text-white ring-4 ring-accent/20'
                      : 'bg-bg-tertiary text-text-tertiary'
                  }`}>
                  {i < currentStep ? <CheckCircle2 className="w-5 h-5" /> : <step.icon className="w-5 h-5" />}
                </div>
                <span className={`text-xs font-semibold mt-2.5 ${i <= currentStep ? 'text-text-primary' : 'text-text-tertiary'}`}>
                  {step.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-4 mt-[-1.5rem] transition-colors duration-500 ${i < currentStep ? 'bg-success' : 'bg-border-primary'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="gemini-card p-5">
        <div className="flex items-center gap-2.5 mb-4 border-b border-border-primary pb-3">
          <div className="flex gap-1.5 z-10">
            <span className="w-2.5 h-2.5 rounded-full bg-accent typing-dot" />
            <span className="w-2.5 h-2.5 rounded-full bg-[#9b51e0] typing-dot" />
            <span className="w-2.5 h-2.5 rounded-full bg-[#e91e63] typing-dot" />
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">Live Activity</span>
        </div>

        <div className="space-y-3.5 max-h-80 overflow-y-auto pr-1">
          {currentStep === 0 && (
            <div className="flex items-center gap-2.5 text-xs text-text-tertiary animate-fadeIn gemini-card p-3.5">
              <span className="w-2 h-2 rounded-full bg-[#4285f4] animate-pulse" />
              Initializing analyst panel...
            </div>
          )}
          {currentStep >= 1 && (
            <div className="flex items-center gap-2.5 text-xs text-success animate-fadeIn gemini-card p-3.5">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              Analyst panel assembled and approved
            </div>
          )}
          {sections.map((_, i) => (
            <div key={i} className="flex items-center gap-2.5 text-xs text-text-secondary animate-fadeIn gemini-card p-3.5" style={{ animationDelay: `${i * 0.1}s` }}>
              <span className="w-2 h-2 rounded-full bg-success shrink-0" />
              Interview {i + 1} completed - section written
            </div>
          ))}
          {currentStep === 1 && sections.length > 0 && (
            <div className="flex items-center gap-2.5 text-xs text-text-tertiary animate-fadeIn gemini-card p-3.5">
              <span className="w-2 h-2 rounded-full bg-[#9b51e0] animate-pulse" />
              Synthesizing final report...
            </div>
          )}
          {currentStep === 2 && sections.length > 0 && (
            <div className="flex items-center gap-2.5 text-xs text-text-tertiary animate-fadeIn gemini-card p-3.5">
              <span className="w-2 h-2 rounded-full bg-[#f2702f] animate-pulse" />
              Compiling report insights...
            </div>
          )}
          {isComplete && (
            <div className="flex items-center gap-2.5 text-xs text-success font-semibold animate-fadeIn gemini-card p-3.5">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              Research complete - report ready
            </div>
          )}
        </div>
      </div>

      {sections.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-xs font-bold text-text-tertiary uppercase tracking-wider pl-1">Completed Sections</h3>
          {sections.map((section, i) => (
            <div key={i} className="gemini-card p-4.5 animate-slideUp" style={{ animationDelay: `${i * 0.15}s` }}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                <span className="text-xs font-bold text-text-primary">Section {i + 1}</span>
              </div>
              <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed font-medium">
                {section.replace(/^##\s+/, "").split("\n")[0]}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ResearchProgress;
