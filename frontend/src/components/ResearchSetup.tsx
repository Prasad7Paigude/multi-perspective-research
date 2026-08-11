import { useState } from 'react';
import { MessageSquare, Users, Sparkles } from 'lucide-react';

interface ResearchSetupProps {
  onStart: (topic: string, maxAnalysts: number, maxTurns: number) => void;
  isLoading: boolean;
}

function ResearchSetup({ onStart, isLoading }: ResearchSetupProps) {
  const [topic, setTopic] = useState('');
  const [maxAnalysts, setMaxAnalysts] = useState(3);
  const [maxTurns, setMaxTurns] = useState(2);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onStart(topic.trim(), maxAnalysts, maxTurns);
  };

  return (
    <div className="animate-fadeIn">
      {/* Hero */}
      <div className="text-center mb-10 pt-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-accent-light mb-5 glass-card">
          <Sparkles className="w-7 h-7 text-accent" />
        </div>
        <h2 className="text-2xl font-semibold text-text-primary tracking-tight mb-2">
          What would you like to explore?
        </h2>
        <p className="text-sm text-text-secondary max-w-md mx-auto leading-relaxed">
          Our AI assembles a diverse panel of expert analysts to examine your topic
          from multiple perspectives and deliver a comprehensive research report.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Research Inquiry */}
        <div className="glass-card p-5">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent-light flex items-center justify-center shrink-0 mt-0.5 glass-card">
              <MessageSquare className="w-4.5 h-4.5 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <label
                htmlFor="topic"
                className="block text-sm font-medium text-text-primary mb-1.5"
              >
                Research Inquiry
              </label>
              <textarea
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., The impact of generative AI on healthcare diagnostics in 2026..."
                rows={3}
                className="w-full px-3.5 py-2.5 text-sm glass-input
                  placeholder:text-text-tertiary text-text-primary
                  focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent
                  transition-colors resize-none"
              />
              <p className="mt-1.5 text-xs text-text-tertiary">
                Describe the subject you'd like analyzed in depth.
              </p>
            </div>
          </div>
        </div>

        {/* Configuration Panel */}
        <div className="glass-card p-5">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent-light flex items-center justify-center shrink-0 mt-0.5 glass-card">
              <Users className="w-4.5 h-4.5 text-accent" />
            </div>
            <div className="flex-1 min-w-0 space-y-5">
              {/* Analyst panel size */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="maxAnalysts" className="text-sm font-medium text-text-primary">
                    Analyst Panel Size
                  </label>
                  <span className="text-sm font-medium text-accent tabular-nums">
                    {maxAnalysts} {maxAnalysts === 1 ? 'analyst' : 'analysts'}
                  </span>
                </div>
                <input
                  id="maxAnalysts"
                  type="range"
                  min={1}
                  max={6}
                  value={maxAnalysts}
                  onChange={(e) => setMaxAnalysts(Number(e.target.value))}
                  className="w-full glass-slider"
                />
                <p className="mt-1.5 text-xs text-text-tertiary">
                  How many expert perspectives should we assemble? (1–6)
                </p>
              </div>

              {/* Interview Depth */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="maxTurns" className="text-sm font-medium text-text-primary">
                    Interview Depth
                  </label>
                  <span className="text-sm font-medium text-accent tabular-nums">
                    {maxTurns} {maxTurns === 1 ? 'round' : 'rounds'}
                  </span>
                </div>
                <input
                  id="maxTurns"
                  type="range"
                  min={1}
                  max={4}
                  value={maxTurns}
                  onChange={(e) => setMaxTurns(Number(e.target.value))}
                  className="w-full glass-slider"
                />
                <p className="mt-1.5 text-xs text-text-tertiary">
                  How many rounds of questioning per analyst? (1–4)
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!topic.trim() || isLoading}
          className="w-full py-3 px-5 rounded-xl glass-btn-primary text-sm font-medium
            disabled:opacity-40 disabled:cursor-not-allowed
            flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Assembling analyst panel...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Begin Research
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default ResearchSetup;