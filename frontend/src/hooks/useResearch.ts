import { useState, useCallback, useRef } from 'react';
import type { SSEEvent, SessionState, ThinkingState } from '../types';

const API_BASE = '/api';

function useResearch() {
  const [state, setState] = useState<SessionState>({
    threadId: null,
    topic: '',
    maxAnalysts: 3,
    maxTurns: 2,
    analysts: [],
    status: 'idle',
    sections: [],
    finalReport: null,
    error: null,
    interviewProgress: { current: 0, total: 0 },
  });
  const [thinkingState, setThinkingState] = useState<ThinkingState | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const initResearch = useCallback(async (topic: string, maxAnalysts: number, maxTurns: number) => {
    setState(prev => ({
      ...prev,
      topic,
      maxAnalysts,
      maxTurns,
      status: 'generating_analysts',
      analysts: [],
      sections: [],
      finalReport: null,
      error: null,
    }));

    try {
      const res = await fetch(`${API_BASE}/research/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, max_analysts: maxAnalysts, max_turns: maxTurns }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || 'Failed to initialize research');
      }

      const data = await res.json();
      setState(prev => ({
        ...prev,
        threadId: data.thread_id,
        analysts: data.analysts,
        status: 'analysts_pending',
      }));
    } catch (err: any) {
      setState(prev => ({ ...prev, status: 'error', error: err.message }));
    }
  }, []);

  const submitFeedback = useCallback(async (feedback: string) => {
    const threadId = state.threadId;
    if (!threadId) return;

    try {
      const res = await fetch(`${API_BASE}/research/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, feedback }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || 'Failed to submit feedback');
      }

      const data = await res.json();
      setState(prev => ({
        ...prev,
        analysts: data.analysts,
        status: 'analysts_pending',
      }));
    } catch (err: any) {
      setState(prev => ({ ...prev, status: 'error', error: err.message }));
    }
  }, [state.threadId]);

  const approveAnalysts = useCallback(async () => {
    const threadId = state.threadId;
    if (!threadId) return;

    try {
      const res = await fetch(`${API_BASE}/research/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || 'Failed to approve analysts');
      }

      setState(prev => ({ ...prev, status: 'interviewing' }));
      startSSEStream(threadId);
    } catch (err: any) {
      setState(prev => ({ ...prev, status: 'error', error: err.message }));
    }
  }, [state.threadId]);

  const startSSEStream = useCallback((threadId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource(`${API_BASE}/research/stream/${threadId}`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);

        switch (data.type) {
          case 'status':
            // Just a status update, keep current state
            break;
          case 'interview_progress':
            setState(prev => ({
              ...prev,
              interviewProgress: data.payload,
            }));
            break;
          case 'thinking_start':
            // Start a new thinking session
            setThinkingState({
              analystName: data.payload.analystName,
              analystRole: data.payload.analystRole,
              content: '',
              isComplete: false,
            });
            break;
          case 'thinking_chunk':
            // Append thinking content in real-time
            setThinkingState(prev => {
              if (prev) {
                return {
                  ...prev,
                  content: prev.content + data.payload.chunk,
                  isComplete: false,
                };
              }
              return null;
            });
            break;
          case 'thinking_complete':
            // Mark current thinking as complete
            setThinkingState(prev => {
              if (prev) {
                return {
                  ...prev,
                  isComplete: true,
                };
              }
              return null;
            });
            break;
           case 'interview_start':
             // Update thinking state with new analyst info when interview starts
             // Don't clear it - we want thinking to show throughout the interview
             setThinkingState({
               analystName: data.payload.analystName || 'Analyst',
               analystRole: data.payload.analystRole || 'Research Analyst',
               content: '',
               isComplete: false,
             });
             break;
          case 'section':
            setState(prev => ({
              ...prev,
              sections: [...prev.sections, data.payload],
            }));
            break;
          case 'report':
            setState(prev => ({
              ...prev,
              sections: [...prev.sections, data.payload],
            }));
            break;
          case 'introduction':
            setState(prev => ({
              ...prev,
              introduction: data.payload,
            }));
            break;
          case 'conclusion':
            setState(prev => ({
              ...prev,
              conclusion: data.payload,
            }));
            break;
          case 'final_report':
            setState(prev => ({
              ...prev,
              finalReport: data.payload,
              status: 'complete',
            }));
            break;
          case 'done':
            es.close();
            eventSourceRef.current = null;
            break;
          case 'error':
            setState(prev => ({
              ...prev,
              status: 'error',
              error: data.payload,
            }));
            es.close();
            eventSourceRef.current = null;
            break;
        }
      } catch (e) {
        // ignore parse errors on incomplete messages
      }
    };

    es.onerror = () => {
      // Check if we already have the final report
      setState(prev => {
        if (prev.finalReport) {
          return { ...prev, status: 'complete' };
        }
        return prev;
      });
      es.close();
      eventSourceRef.current = null;
    };
  }, []);

  const reset = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setState({
      threadId: null,
      topic: '',
      maxAnalysts: 3,
      maxTurns: 2,
      analysts: [],
      status: 'idle',
      sections: [],
      finalReport: null,
      error: null,
      interviewProgress: { current: 0, total: 0 },
    });
    setThinkingState(null);
  }, []);

  return {
    ...state,
    thinkingState,
    initResearch,
    submitFeedback,
    approveAnalysts,
    reset,
  };
}

export default useResearch;