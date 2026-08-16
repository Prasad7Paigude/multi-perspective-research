import { useState, useEffect, useRef, useCallback } from 'react';

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

// Ease-out quadratic function for deceleration
const easeOutQuad = (t: number): number => 1 - (1 - t) * (1 - t);

interface SimulatedProgressResult {
  progress: number; // 0-100 (capped at 90 until completion)
  statusText: string;
  start: () => void;
  complete: () => void;
  reset: () => void;
  isAnimatingToComplete: boolean;
}

export function useSimulatedProgress(estimatedDurationMs: number = ESTIMATED_DURATION_MS): SimulatedProgressResult {
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState(STATUS_MESSAGES[0]);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isAnimatingToComplete, setIsAnimatingToComplete] = useState(false);
  
  const startTimeRef = useRef<number | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const statusIntervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const progressRef = useRef<number>(0);

  const setProgressWithRef = (val: number) => {
    progressRef.current = val;
    setProgress(val);
  };

  // Rotate status text with irregular timing (4-8 seconds)
  useEffect(() => {
    if (!isRunning) return;
    
    const rotateStatus = () => {
      const randomIndex = Math.floor(Math.random() * STATUS_MESSAGES.length);
      setStatusText(STATUS_MESSAGES[randomIndex]);
      
      // Random interval between 4-8 seconds for natural feel
      const nextInterval = 4000 + Math.random() * 4000;
      statusIntervalRef.current = setTimeout(rotateStatus, nextInterval);
    };
    
    statusIntervalRef.current = setTimeout(rotateStatus, 4000 + Math.random() * 4000);
    
    return () => {
      if (statusIntervalRef.current) {
        clearTimeout(statusIntervalRef.current);
      }
    };
  }, [isRunning]);

  // Update progress based on elapsed time with pronounced irregular pacing and random step sizes
  useEffect(() => {
    if (!isRunning || isComplete || isAnimatingToComplete) return;
    
    let timerId: ReturnType<typeof setTimeout> | null = null;
    
    const updateProgressTick = () => {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now();
      }
      
      const elapsed = Date.now() - startTimeRef.current;
      
      // Calculate eased target progress (0 to 90)
      const t = Math.min(1, elapsed / estimatedDurationMs);
      const targetProgress = easeOutQuad(t) * 90;
      
      const current = progressRef.current;
      if (current < targetProgress) {
        // Step size varies randomly between 0.5% and 8%
        const maxStep = targetProgress - current;
        const randomStep = 0.5 + Math.random() * 7.5;
        const step = Math.min(maxStep, randomStep);
        
        setProgressWithRef(Math.min(90, current + step));
      }
      
      // Pronounced irregular timing:
      // 70% chance of a quick succession update (200-400ms)
      // 30% chance of a long pause (1.5 - 3.0s)
      const isQuick = Math.random() < 0.7;
      const nextDelay = isQuick 
        ? 200 + Math.random() * 200 
        : 1500 + Math.random() * 1500;
        
      timerId = setTimeout(updateProgressTick, nextDelay);
    };
    
    // First update tick
    timerId = setTimeout(updateProgressTick, 200 + Math.random() * 200);
    
    return () => {
      if (timerId) {
        clearTimeout(timerId);
      }
    };
  }, [isRunning, isComplete, isAnimatingToComplete, estimatedDurationMs]);

  // Start the simulated progress
  const start = () => {
    setIsRunning(true);
    setIsComplete(false);
    setProgressWithRef(0);
    startTimeRef.current = Date.now();
  };

  // Animate to 100% completion
  const animateToComplete = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    const startProgress = progressRef.current;
    const startTime = Date.now();
    const duration = 500; // 500ms transition to 100%
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const t = Math.min(1, elapsed / duration);
      
      // Ease-out for smooth deceleration
      const easedT = easeOutQuad(t);
      const newProgress = startProgress + (100 - startProgress) * easedT;
      
      setProgressWithRef(newProgress);
      setIsAnimatingToComplete(true);
      
      if (t < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        setProgressWithRef(100);
        setIsAnimatingToComplete(false);
        setIsComplete(true);
        setIsRunning(false);
        setStatusText('Report ready!');
      }
    };
    
    animationFrameRef.current = requestAnimationFrame(animate);
  }, []);

  // Complete the progress (animate to 100%)
  const complete = () => {
    setIsRunning(false);
    
    // Clean up timeouts
    if (statusIntervalRef.current) {
      clearTimeout(statusIntervalRef.current);
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    // Animate to 100
    animateToComplete();
  };

  // Reset the progress
  const reset = () => {
    setIsRunning(false);
    setIsComplete(false);
    setProgressWithRef(0);
    setStatusText(STATUS_MESSAGES[0]);
    startTimeRef.current = null;
    
    if (statusIntervalRef.current) {
      clearTimeout(statusIntervalRef.current);
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
    isAnimatingToComplete,
  };
}

export { ESTIMATED_DURATION_MS, STATUS_MESSAGES };
