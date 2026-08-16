import { useState } from 'react';
import { FileText, Copy, Download, Check, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface FinalReportProps {
  report: string;
  sections: string[];
  topic: string;
  onReset: () => void;
  analysts: any[];
}

function FinalReport({ report, sections, topic, onReset, analysts }: FinalReportProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${topic.slice(0, 40).toLowerCase().replace(/\s+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-fadeIn">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-success-light flex items-center justify-center gemini-card shrink-0">
            <FileText className="w-5 h-5 text-success" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-text-primary tracking-tight">Research Report</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Comprehensive analysis for <strong className="font-semibold text-text-primary">"{topic}"</strong>
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2.5 mb-6">
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-full gemini-btn-secondary text-xs font-semibold text-text-secondary transition-colors cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-success" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              Copy Report
            </>
          )}
        </button>
        <button
          onClick={handleDownload}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-full gemini-btn-secondary text-xs font-semibold text-text-secondary transition-colors cursor-pointer"
        >
          <Download className="w-3.5 h-3.5" />
          Download Markdown
        </button>
        <button
          onClick={onReset}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-full gemini-btn-secondary text-xs font-semibold text-text-secondary transition-colors ml-auto cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          New Research
        </button>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="px-3.5 py-1.5 rounded-xl gemini-card">
          <span className="text-xs text-text-secondary">
            <span className="font-bold text-text-primary">{analysts?.length || sections.length}</span> analyst perspectives
          </span>
        </div>
        <div className="px-3.5 py-1.5 rounded-xl gemini-card">
          <span className="text-xs text-text-secondary">
            <span className="font-bold text-text-primary">{report.split(/\s+/).length}</span> words
          </span>
        </div>
      </div>

      <div className="gemini-card p-6 md:p-8">
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report}
          </ReactMarkdown>
        </div>
      </div>

      {sections.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xs font-bold text-text-tertiary uppercase tracking-wider mb-3 pl-1">
            Individual Analyst Perspectives
          </h3>
          <div className="space-y-3">
            {sections.map((section, i) => (
              <details
                key={i}
                className="gemini-card overflow-hidden group"
              >
                <summary className="px-5 py-3.5 cursor-pointer text-sm font-semibold text-text-primary hover:bg-surface-hover transition-colors flex items-center gap-2 [&::-webkit-details-marker]:hidden">
                  <span className="w-5 h-5 rounded-full bg-accent-light flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold bg-gradient-to-r from-[#4285f4] to-[#9b51e0] bg-clip-text text-transparent">{i + 1}</span>
                  </span>
                  {section.replace(/^##\s+/, '').split('\n')[0] || `Perspective ${i + 1}`}
                </summary>
                <div className="px-5 pb-4 border-t border-border-primary">
                  <div className="pt-4 markdown-body text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {section}
                    </ReactMarkdown>
                  </div>
                </div>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FinalReport;
