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
  const lastUpdateTimeRef = useRef<number | null>(null);

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

  // Update progress based on elapsed time with natural irregularity
  useEffect(() => {
    if (!isRunning || isComplete || isAnimatingToComplete) return;
    
    const updateProgress = () => {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now();
        lastUpdateTimeRef.current = Date.now();
      }
      
      const elapsed = Date.now() - startTimeRef.current;
      const now = Date.now();
      
      // Add natural jitter: only update every 50-200ms (not every frame)
      if (lastUpdateTimeRef.current && now - lastUpdateTimeRef.current < 50 + Math.random() * 150) {
        animationFrameRef.current = requestAnimationFrame(updateProgress);
        return;
      }
      
      lastUpdateTimeRef.current = now;
      
      // Calculate base progress with easing
      let baseProgress = (elapsed / estimatedDurationMs);
      
      // Apply ease-out for deceleration
      baseProgress = easeOutQuad(Math.min(1, baseProgress));
      
      // Cap at 90% until completion, with small random jitter
      let newProgress = Math.min(90, baseProgress * 100);
      
      // Add small random jitter to make it feel more natural
      const jitter = (Math.random() - 0.5) * 0.5; // -0.25% to +0.25%
      newProgress = Math.max(0, Math.min(90, newProgress + jitter));
      
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
  }, [isRunning, isComplete, isAnimatingToComplete, estimatedDurationMs]);

  // Start the simulated progress
  const start = () => {
    setIsRunning(true);
    setIsComplete(false);
    setProgress(0);
    startTimeRef.current = Date.now();
  };

  // Animate to 100% completion
  const animateToComplete = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    const startProgress = progress;
    const startTime = Date.now();
    const duration = 400; // 400ms animation
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const t = Math.min(1, elapsed / duration);
      
      // Ease-out for smooth deceleration
      const easedT = easeOutQuad(t);
      const newProgress = startProgress + (100 - startProgress) * easedT;
      
      setProgress(newProgress);
      setIsAnimatingToComplete(true);
      
      if (t < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        setProgress(100);
        setIsAnimatingToComplete(false);
        setIsComplete(true);
        setIsRunning(false);
        setStatusText('Report ready!');
      }
    };
    
    animationFrameRef.current = requestAnimationFrame(animate);
  }, [progress]);

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
    
    // Animate to 100%
    animateToComplete();
  };

  // Reset the progress
  const reset = () => {
    setIsRunning(false);
    setIsComplete(false);
    setProgress(0);
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
