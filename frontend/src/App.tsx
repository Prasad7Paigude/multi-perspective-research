import Header from './components/Header';
import ResearchSetup from './components/ResearchSetup';
import AnalystReview from './components/AnalystReview';
import ResearchProgress from './components/ResearchProgress';
import FinalReport from './components/FinalReport';
import useResearch from './hooks/useResearch';

function App() {
  const {
    topic,
    analysts,
    sections,
    finalReport,
    status,
    error,
    initResearch,
    submitFeedback,
    approveAnalysts,
    reset,
  } = useResearch();

  // Real completion is driven solely by the backend `final_report` SSE event
  // (reflected here as status === 'complete'). During the run the stage
  // indicator advances from the live simulated progress; only genuine report
  // arrival flips it to the all-complete state.
  const isComplete = status === 'complete';

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col relative z-0">
      {/* Gemini Drifting Blobs Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-[-1]">
        <div className="absolute w-[350px] md:w-[550px] h-[350px] md:h-[550px] rounded-full bg-blue-500/8 dark:bg-blue-500/12 blur-[90px] md:blur-[120px] animate-blob-1 top-[-10%] left-[-10%]" />
        <div className="absolute w-[400px] md:w-[650px] h-[400px] md:h-[650px] rounded-full bg-purple-500/8 dark:bg-purple-500/12 blur-[100px] md:blur-[130px] animate-blob-2 bottom-[-10%] right-[-10%]" />
        <div className="absolute w-[300px] md:w-[500px] h-[300px] md:h-[500px] rounded-full bg-pink-500/8 dark:bg-pink-500/12 blur-[80px] md:blur-[110px] animate-blob-3 top-[25%] right-[5%]" />
      </div>

      <Header />

      <main className="flex-1 max-w-2xl w-full mx-auto px-6 py-8 relative z-10">
        {status === 'idle' && (
          <ResearchSetup
            onStart={initResearch}
            isLoading={false}
          />
        )}

        {status === 'generating_analysts' && (
          <div className="animate-fadeIn text-center pt-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent-light mb-6 gemini-card relative overflow-hidden">
              <div className="absolute inset-0 animate-shimmer" />
              <span className="w-6 h-6 border-2 border-accent/30 border-t-accent rounded-full animate-spin z-10" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2 tracking-tight">
              Assembling Analyst Panel
            </h2>
            <p className="text-sm text-text-secondary max-w-sm mx-auto">
              Our AI is composing a diverse panel of expert perspectives tailored to your inquiry.
            </p>
          </div>
        )}

        {status === 'analysts_pending' && analysts.length > 0 && (
          <AnalystReview
            analysts={analysts}
            topic={topic}
            onFeedback={submitFeedback}
            onApprove={approveAnalysts}
            isProcessing={false}
          />
        )}

        {(status === 'interviewing' || (status === 'complete' && !finalReport)) && (
          <ResearchProgress
            sections={sections}
            isComplete={isComplete}
          />
        )}

        {status === 'complete' && finalReport && (
          <FinalReport
            report={finalReport}
            sections={sections}
            topic={topic}
            onReset={reset}
            analysts={analysts}
          />
        )}

        {status === 'error' && (
          <div className="animate-fadeIn text-center pt-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-warning-light mb-6 gemini-card">
              <span className="text-2xl">⚠</span>
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2 tracking-tight">
              Something went wrong
            </h2>
            <p className="text-sm text-text-secondary max-w-md mx-auto mb-6">
              {error || 'An unexpected error occurred. Please try again.'}
            </p>
            <button
              onClick={reset}
              className="px-6 py-3 rounded-full gemini-btn-primary text-sm font-medium
                disabled:opacity-40 disabled:cursor-not-allowed
                transition-all duration-200"
            >
              Try Again
            </button>
          </div>
        )}
      </main>

      <footer className="border-t border-border-primary py-6 relative z-10 bg-surface-bg">
        <p className="text-xs text-text-tertiary text-center">
          Research Assistant — AI-Powered Multi-Perspective Analysis
        </p>
      </footer>
    </div>
  );
}

export default App;
