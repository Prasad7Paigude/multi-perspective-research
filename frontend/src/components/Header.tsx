import { Sparkles } from 'lucide-react';

function Header() {
  return (
    <header className="border-b border-border-primary bg-bg-secondary">
      <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div>
          <h1 className="text-base font-medium text-text-primary tracking-tight">
            Research Assistant
          </h1>
          <p className="text-xs text-text-tertiary">
            AI-Powered Multi-Perspective Analysis
          </p>
        </div>
      </div>
    </header>
  );
}

export default Header;