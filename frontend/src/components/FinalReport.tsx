import { useState, useMemo } from 'react';
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

/**
 * Detects the "## Sources" (or "### Sources") section in a markdown string,
 * converts [N] entries into proper markdown list items, and truncates long
 * URLs in the display text while keeping the full URL as the link target.
 *
 * The result is a markdown string where each source entry is a list item
 * with a clickable link. Long URLs are displayed with "..." truncation.
 */
function formatSourcesForMarkdown(content: string): string {
  if (!content) return content;

  // Match a Sources heading (## or ###) and capture everything until the next
  // heading at the same or higher level, or end of string.
  const sourceSectionPattern = /(#{2,3}\s+Sources\s*\n)([\s\S]*?)(?=\n#{1,3}\s+|$)/i;

  const match = content.match(sourceSectionPattern);
  if (!match) return content;

  const header = match[1];
  const body = match[2];

  // Parse individual [N] source entries - one per line or separated by [N] markers
  // The regex matches [N] followed by text up to the next [M] marker or end of line
  const entryPattern = /\[(\d+)\]\s+(.+?)(?=\s*\[\d+\]|\n|$)/g;
  const entries: Array<{ num: string; text: string }> = [];
  let entryMatch;
  while ((entryMatch = entryPattern.exec(body)) !== null) {
    const num = entryMatch[1];
    const text = entryMatch[2].trim();
    if (text) {
      entries.push({ num, text });
    }
  }

  if (entries.length === 0) return content;

  // Rebuild the sources section as a markdown list with truncated links
  const MAX_DISPLAY_LENGTH = 80; // Truncate URL display text to 80 chars
  const listItems = entries.map(({ num, text }) => {
    return `- [${num}] ${truncateUrlDisplay(text, MAX_DISPLAY_LENGTH)}`;
  });

  const newSection = header + listItems.join('\n') + '\n';

  const matchIndex = match.index ?? 0;
  return content.slice(0, matchIndex) + newSection + content.slice(matchIndex + match[0].length);
}

/**
 * If the text contains a URL, returns a markdown link where the display text
 * is truncated with "..." if it exceeds the max length, but the full URL is
 * preserved as the href. If no URL is found, returns the original text.
 */
function truncateUrlDisplay(text: string, maxLength: number): string {
  // Try to extract a URL from the text
  const urlMatch = text.match(/https?:\/\/[^\s]+/);
  if (!urlMatch) {
    // No URL found — just truncate with ellipsis if too long
    if (text.length > maxLength) {
      return text.slice(0, maxLength) + '...';
    }
    return escapeMarkdownLink(text);
  }

  const fullUrl = urlMatch[0];
  const urlIndex = urlMatch.index ?? 0;
  const restOfText = text.slice(0, urlIndex) + text.slice(urlIndex + fullUrl.length);

  // Truncate the URL for display if it's long
  let displayUrl = fullUrl;
  if (fullUrl.length > maxLength) {
    displayUrl = fullUrl.slice(0, maxLength) + '...';
  }

  // If there's additional text before/after the URL, include it in the display
  const displayText = (restOfText.trim() + ' ' + displayUrl).trim();
  const cleanedDisplay = displayText.replace(/\s+/g, ' ');

  // Return as a markdown link: [cleanedDisplay](fullUrl)
  // Escape any ] in the display text to avoid breaking the markdown link
  const escapedDisplay = cleanedDisplay.replace(/\]/g, '\\]');
  // Escape parentheses in URL portion to avoid breaking markdown links
  const escapedUrl = fullUrl.replace(/[()]/g, m => encodeURIComponent(m));

  return `[${escapedDisplay}](${escapedUrl})`;
}

/**
 * Escapes characters that could break markdown link syntax.
 */
function escapeMarkdownLink(text: string): string {
  return text.replace(/\]/g, '\\]').replace(/\[/g, '\\[');
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

  // Extract the title from the first markdown heading line (e.g. "# Title")
  // and strip ALL leading '#' markers (handles doubled/LLM-emitted hashes such
  // as "# # Title" or "## Title") so the title never renders a literal '#'.
  // Also format the Sources section as proper markdown list items with
  // truncated URL display text.
  const { reportTitle, reportBody } = useMemo(() => {
    const titleMatch = report.match(/^#{1,6}(?:\s*#*)?\s+(.+)$/m);
    if (titleMatch) {
      const title = titleMatch[1].replace(/^#+\s*/, '').trim();
      const body = report.slice(titleMatch[0].length).replace(/^\n+/, '');
      const formattedBody = formatSourcesForMarkdown(body);
      return { reportTitle: title, reportBody: formattedBody };
    }
    return { reportTitle: null, reportBody: formatSourcesForMarkdown(report) };
  }, [report]);

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

      {/* Extracted title displayed as a styled H1 (no literal #) */}
      {reportTitle && (
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-text-primary tracking-tight leading-tight">
            {reportTitle}
          </h1>
        </div>
      )}

      <div className="gemini-card p-6 md:p-8">
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {reportBody}
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
                    <span className="text-xs font-bold bg-gradient-to-r from-[#4285f4] to-[#9b51e5] bg-clip-text text-transparent">{i + 1}</span>
                  </span>
                  {section.replace(/^##\s+/, '').split('\n')[0] || `Perspective ${i + 1}`}
                </summary>
                <div className="px-5 pb-4 border-t border-border-primary">
                  <div className="pt-4 markdown-body text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {formatSourcesForMarkdown(section)}
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
