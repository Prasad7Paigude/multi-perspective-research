import { useEffect, useImperativeHandle, forwardRef } from 'react';
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

  useImperativeHandle(ref, () => ({
    complete: () => {
      complete();
      if (onComplete) onComplete();
    }
  }));

  // Start progress when component mounts
  useEffect(() => {
    start();
    return () => {
      reset();
    };
  }, []);

  // Notify parent when progress reaches 100%
  useEffect(() => {
    if (progress >= 100 && onComplete) {
      onComplete();
    }
  }, [progress, onComplete]);

  return (
    <div className="w-full">
      {/* Progress Bar Container */}
      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1 text-text-primary">
          <span>Research Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        
        {/* Progress Bar */}
        <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden glass">
          <div
            className="h-full bg-accent transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Status Text */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex gap-1">
          <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
          <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
          <span className="w-2 h-2 rounded-full bg-accent typing-dot" />
        </div>
        <span className="text-sm font-medium text-text-secondary">
          {statusText}
        </span>
      </div>
    </div>
  );
}

export default forwardRef(SimulatedProgressBar);
