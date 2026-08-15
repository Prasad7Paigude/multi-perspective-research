import { useEffect, useImperativeHandle, useRef, forwardRef } from 'react';
import { useSimulatedProgress } from '../hooks/useSimulatedProgress';

interface SimulatedProgressBarProps {
  onComplete?: () => void;
  estimatedDurationMs?: number;
}

export interface SimulatedProgressBarHandle {
  complete: () => void;
}

export function SimulatedProgressBar({ 
  onComplete, 
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
      <div className="mb-2">
        <div className="flex justify-between text-xs mb-1 text-text-primary">
          <span>Research Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        
        {/* Progress Bar */}
        <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            ref={progressFillRef}
            className="h-full bg-accent transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Status Text */}
      <div className="text-sm font-medium text-text-secondary">
        {statusText}
      </div>
    </div>
  );
}

export default forwardRef(SimulatedProgressBar);
