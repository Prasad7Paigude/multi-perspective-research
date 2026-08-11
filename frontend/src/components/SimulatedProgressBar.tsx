import { useEffect } from 'react';
import { useSimulatedProgress } from '../hooks/useSimulatedProgress';

interface SimulatedProgressBarProps {
  onComplete?: () => void;
  estimatedDurationMs?: number;
}

export function SimulatedProgressBar({ 
  onComplete, 
  estimatedDurationMs 
}: SimulatedProgressBarProps) {
  const { progress, statusText, start, reset } = useSimulatedProgress(estimatedDurationMs);

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
        
        {/* Ambient Animation (subtle shimmer) */}
        <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden relative">
          <div className="absolute inset-0 animate-shimmer" />
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

      {/* Ambient Pulse Element */}
      <div className="flex justify-center">
        <div className="w-4 h-4 rounded-full bg-accent/20 animate-pulse-soft" />
      </div>
    </div>
  );
}

export default SimulatedProgressBar;
