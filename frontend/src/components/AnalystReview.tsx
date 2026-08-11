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
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center glass-card">
          <Users className="w-5 h-5 text-accent" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            Analyst Panel Review
          </h2>
          <p className="text-sm text-text-secondary">
            Review the assembled expert panel for your inquiry on <strong className="font-medium text-text-primary">"{topic}"</strong>
          </p>
        </div>
      </div>

      {/* Analyst Cards */}
      <div className="grid gap-3 mb-6">
        {analysts.map((analyst, i) => (
          <AnalystCard key={analyst.name} analyst={analyst} index={i} />
        ))}
      </div>

      {/* Feedback Section */}
      <div className="glass-card p-5 mb-4">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent-light flex items-center justify-center shrink-0 mt-0.5 glass-card">
            <MessageSquare className="w-4.5 h-4.5 text-accent" />
          </div>
          <div className="flex-1 min-w-0">
            <label
              htmlFor="feedback"
              className="block text-sm font-medium text-text-primary mb-1.5"
            >
              Refinement Guidance
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="e.g., Add someone with a regulatory perspective, or include a critic of this technology..."
              rows={2}
              className="w-full px-3.5 py-2.5 text-sm glass-input
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
      <div className="flex items-center gap-3">
        <button
          onClick={handleRefine}
          disabled={!feedback.trim() || isRefining}
          className="flex-1 py-2.5 px-4 rounded-xl glass-btn-secondary
            text-sm font-medium text-text-primary
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
          className="flex-[2] py-2.5 px-4 rounded-xl glass-btn-primary text-sm font-medium
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