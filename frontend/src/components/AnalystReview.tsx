import { useState } from 'react';
import { Users, MessageSquare, ArrowRight, RotateCcw } from 'lucide-react';
import type { Analyst } from '../types';
import AnalystCard from './AnalystCard';

interface AnalystReviewProps {
  analysts: Analyst[];
  topic: string;
  onFeedback: (feedback: string) => Promise<void>;
  onApprove: () => Promise<void>;
  isProcessing: boolean;
}

function AnalystReview({ analysts, topic, onFeedback, onApprove, isProcessing }: AnalystReviewProps) {
  const [feedback, setFeedback] = useState('');
  const [isRefining, setIsRefining] = useState(false);

  const handleRefine = async () => {
    if (!feedback.trim()) return;
    setIsRefining(true);
    await onFeedback(feedback.trim());
    setFeedback('');
    setIsRefining(false);
  };

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-3.5 mb-6">
        <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center gemini-card shrink-0">
          <Users className="w-5 h-5 text-[#4285f4]" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-text-primary tracking-tight">
            Analyst Panel Review
          </h2>
          <p className="text-sm text-text-secondary leading-relaxed">
            Review the assembled expert panel for your inquiry on <strong className="font-semibold text-text-primary">"{topic}"</strong>
          </p>
        </div>
      </div>

      {/* Analyst Cards */}
      <div className="grid gap-4 mb-6">
        {analysts.map((analyst, i) => (
          <AnalystCard key={analyst.name} analyst={analyst} index={i} />
        ))}
      </div>

      {/* Feedback Section */}
      <div className="gemini-card p-5 mb-5">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent-light flex items-center justify-center shrink-0 mt-0.5 gemini-card">
            <MessageSquare className="w-4.5 h-4.5 text-[#9b51e0]" />
          </div>
          <div className="flex-1 min-w-0">
            <label
              htmlFor="feedback"
              className="block text-sm font-semibold text-text-primary mb-1.5"
            >
              Refinement Guidance
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="e.g., Add someone with a regulatory perspective, or include a critic of this technology..."
              rows={2}
              className="w-full px-4 py-3 text-sm gemini-input
                placeholder:text-text-tertiary text-text-primary
                focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent
                transition-colors resize-none"
            />
            <p className="mt-1.5 text-xs text-text-tertiary">
              Optionally provide direction to adjust the panel composition before proceeding.
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleRefine}
          disabled={!feedback.trim() || isRefining}
          className="flex-1 py-3 px-5 rounded-full gemini-btn-secondary
            text-sm font-semibold text-text-primary cursor-pointer
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200 flex items-center justify-center gap-2"
        >
          {isRefining ? (
            <>
              <span className="w-4 h-4 border-2 border-text-tertiary border-t-text-primary rounded-full animate-spin" />
              Refining...
            </>
          ) : (
            <>
              <RotateCcw className="w-4 h-4" />
              Refine Panel
            </>
          )}
        </button>
        <button
          onClick={onApprove}
          disabled={isProcessing}
          className="flex-[1.8] py-3 px-5 rounded-full gemini-btn-primary text-sm font-semibold cursor-pointer
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200
            flex items-center justify-center gap-2"
        >
          {isProcessing ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Starting Analysis...
            </>
          ) : (
            <>
              Proceed with Analysis
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default AnalystReview;