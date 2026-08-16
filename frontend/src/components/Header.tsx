import { Sparkles } from 'lucide-react';

function Header() {
  return (
    <header className="bg-surface-bg border-b border-border-primary shadow-sm sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3.5">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#4285f4] via-[#9b51e0] to-[#e91e63] flex items-center justify-center shadow-md shadow-accent/10">
          <Sparkles className="w-4.5 h-4.5 text-white" />
        </div>
        <div>
          <h1 className="text-base font-bold text-text-primary tracking-tight bg-gradient-to-r from-[#4285f4] via-[#9b51e0] to-[#e91e63] bg-clip-text text-transparent">
            Research Assistant
          </h1>
          <p className="text-[10px] uppercase font-semibold tracking-wider text-text-tertiary">
            AI-Powered Multi-Perspective Analysis
          </p>
        </div>
      </div>
    </header>
  );
}

export default Header;