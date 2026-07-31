export interface Analyst {
  name: string;
  role: string;
  affiliation: string;
  description: string;
  persona: string;
}

export interface ResearchInitResponse {
  thread_id: string;
  status: string;
  analysts: Analyst[];
}

export interface SSEEvent {
  type: 'analysts' | 'section' | 'report' | 'introduction' | 'conclusion' | 'final_report' | 'status' | 'done' | 'error' |
        'thinking_start' | 'thinking_chunk' | 'thinking_complete' | 'interview_start' | 'interview_progress';
  payload: any;
}

export interface ThinkingState {
  analystName: string;
  analystRole: string;
  content: string;
  isComplete: boolean;
}

export interface SessionState {
  threadId: string | null;
  topic: string;
  maxAnalysts: number;
  maxTurns: number;
  analysts: Analyst[];
  status: 'idle' | 'generating_analysts' | 'analysts_pending' | 'interviewing' | 'complete' | 'error';
  sections: string[];
  finalReport: string | null;
  error: string | null;
  introduction?: string;
  conclusion?: string;
  interviewProgress?: { current: number; total: number };
}
