import { useEffect, useImperativeHandle, useRef, forwardRef } from 'react';
import { useSimulatedProgress } from '../hooks/useSimulatedProgress';

interface SimulatedProgressBarProps {
  onComplete?: () => void;
  onProgress?: (progress: number) => void;
  estimatedDurationMs?: number;
}

export interface SimulatedProgressBarHandle {
  complete: () => void;
}

export function SimulatedProgressBar({ 
  onComplete, 
  onProgress,
  estimatedDurationMs 
}: SimulatedProgressBarProps, ref: any) {
  const { progress, statusText, start, reset, complete } = useSimulatedProgress(estimatedDurationMs);
  const progressFillRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({
    complete: () => {
      complete();
    }
  }));

  // Start progress when component mounts
  useEffect(() => {
    start();
    return () => {
      reset();
    };
  }, []);

  // Notify parent of progress changes
  useEffect(() => {
    if (onProgress) {
      onProgress(progress);
    }
  }, [progress, onProgress]);

  // Listen for transitionend on progress fill to sync with visual completion
  useEffect(() => {
    const fillElement = progressFillRef.current;
    if (!fillElement || !onComplete) return;

    const handleTransitionEnd = (e: TransitionEvent) => {
      // Only trigger when the width transition completes and we're at 100%
      if (e.propertyName === 'width' && progress >= 100) {
        onComplete();
      }
    };

    fillElement.addEventListener('transitionend', handleTransitionEnd);
    return () => {
      fillElement.removeEventListener('transitionend', handleTransitionEnd);
    };
  }, [progress, onComplete]);

  return (
    <div className="w-full">
      {/* Progress Bar Container */}
      <div className="mb-3">
        <div className="flex justify-between text-xs font-bold uppercase tracking-wider mb-2 text-text-secondary">
          <span>Research Progress</span>
          <span className="bg-accent-light px-2 py-0.5 rounded-full text-accent font-semibold">{Math.round(progress)}%</span>
        </div>
        
        {/* Progress Bar */}
        <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden shadow-inner">
          <div
            ref={progressFillRef}
            className="h-full transition-all duration-300 ease-out"
            style={{ 
              width: `${progress}%`,
              background: 'var(--gradient-gemini)'
            }}
          />
        </div>
      </div>

      {/* Status Text */}
      <div className="text-sm font-semibold text-text-primary bg-bg-secondary/40 px-3 py-2.5 rounded-xl border border-border-primary inline-block">
        <span className="inline-block animate-pulse mr-2">✦</span>
        {statusText}
      </div>
    </div>
  );
}

export default forwardRef(SimulatedProgressBar);
