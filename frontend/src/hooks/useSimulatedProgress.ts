import { useState, useEffect, useRef } from 'react';

// Default estimated duration for the interview phase (120 seconds = 2 minutes)
const ESTIMATED_DURATION_MS = 120000;

// Status messages to rotate during the interview phase
const STATUS_MESSAGES = [
  'Reviewing the topic...',
  'Consulting expert sources...',
  'Cross-referencing findings...',
  'Synthesizing perspectives...',
  'Drafting the report...',
];

interface SimulatedProgressResult {
  progress: number; // 0-100 (capped at 90 until completion)
  statusText: string;
  start: () => void;
  complete: () => void;
  reset: () => void;
}

export function useSimulatedProgress(estimatedDurationMs: number = ESTIMATED_DURATION_MS): SimulatedProgressResult {
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState(STATUS_MESSAGES[0]);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  
  const startTimeRef = useRef<number | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const statusIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Rotate status text every 6 seconds
  useEffect(() => {
    if (!isRunning) return;
    
    statusIntervalRef.current = setInterval(() => {
      const randomIndex = Math.floor(Math.random() * STATUS_MESSAGES.length);
      setStatusText(STATUS_MESSAGES[randomIndex]);
    }, 6000);
    
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, [isRunning]);

  // Update progress based on elapsed time
  useEffect(() => {
    if (!isRunning || isComplete) return;
    
    const updateProgress = () => {
      if (!startTimeRef.current) return;
      
      const elapsed = Date.now() - startTimeRef.current;
      // Cap at 90% until completion
      const newProgress = Math.min(90, (elapsed / estimatedDurationMs) * 100);
      setProgress(newProgress);
      
      // Continue the animation loop
      animationFrameRef.current = requestAnimationFrame(updateProgress);
    };
    
    // Start the animation loop
    animationFrameRef.current = requestAnimationFrame(updateProgress);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRunning, isComplete, estimatedDurationMs]);

  // Start the simulated progress
  const start = () => {
    setIsRunning(true);
    setIsComplete(false);
    setProgress(0);
    startTimeRef.current = Date.now();
  };

  // Complete the progress (jump to 100%)
  const complete = () => {
    setIsRunning(false);
    setIsComplete(true);
    setProgress(100);
    
    // Clean up intervals
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current);
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  // Reset the progress
  const reset = () => {
    setIsRunning(false);
    setIsComplete(false);
    setProgress(0);
    setStatusText(STATUS_MESSAGES[0]);
    startTimeRef.current = null;
    
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current);
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  return {
    progress,
    statusText,
    start,
    complete,
    reset,
  };
}

export { ESTIMATED_DURATION_MS, STATUS_MESSAGES };
