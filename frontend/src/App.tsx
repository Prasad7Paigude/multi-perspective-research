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
    thinkingState,
    initResearch,
    submitFeedback,
    approveAnalysts,
    reset,
  } = useResearch();

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col">
      <Header />

      <main className="flex-1 max-w-2xl w-full mx-auto px-6 py-8">
        {/* Status: idle → show setup */}
        {status === 'idle' && (
          <ResearchSetup
            onStart={initResearch}
            isLoading={false}
          />
        )}

        {/* Status: generating_analysts */}
        {status === 'generating_analysts' && (
          <div className="animate-fadeIn text-center pt-16">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-accent-light mb-5">
              <span className="w-6 h-6 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
            </div>
            <h2 className="text-lg font-semibold text-text-primary mb-2">
              Assembling Analyst Panel
            </h2>
            <p className="text-sm text-text-secondary max-w-sm mx-auto">
              Our AI is composing a diverse panel of expert perspectives tailored to your inquiry.
            </p>
          </div>
        )}

        {/* Status: analysts_pending → show review */}
        {status === 'analysts_pending' && analysts.length > 0 && (
          <AnalystReview
            analysts={analysts}
            topic={topic}
            onFeedback={submitFeedback}
            onApprove={approveAnalysts}
            isProcessing={false}
          />
        )}

        {/* Status: interviewing → show progress */}
        {status === 'interviewing' && (
          <ResearchProgress
            sections={sections}
            isComplete={false}
            thinkingState={thinkingState}
          />
        )}

         {/* Status: complete → show report */}
         {status === 'complete' && finalReport && (
           <FinalReport
             report={finalReport}
             sections={sections}
             topic={topic}
             onReset={reset}
             analysts={analysts}
           />
         )}

        {/* Status: error */}
        {status === 'error' && (
          <div className="animate-fadeIn text-center pt-16">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-warning-light mb-5">
              <span className="text-2xl">⚠</span>
            </div>
            <h2 className="text-lg font-semibold text-text-primary mb-2">
              Something went wrong
            </h2>
            <p className="text-sm text-text-secondary max-w-md mx-auto mb-6">
              {error || 'An unexpected error occurred. Please try again.'}
            </p>
            <button
              onClick={reset}
              className="px-5 py-2.5 rounded-xl bg-accent text-white text-sm font-medium
                hover:bg-accent-hover transition-all duration-200"
            >
              Try Again
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border-primary py-4">
        <p className="text-xs text-text-tertiary text-center">
          Research Assistant — AI-Powered Multi-Perspective Analysis
        </p>
      </footer>
    </div>
  );
}

export default App;