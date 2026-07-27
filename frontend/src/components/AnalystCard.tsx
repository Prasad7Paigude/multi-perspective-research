import { User, Building2, Target } from 'lucide-react';
import type { Analyst } from '../types';

interface AnalystCardProps {
  analyst: Analyst;
  index: number;
}

function AnalystCard({ analyst, index }: AnalystCardProps) {
  return (
    <div className="animate-slideUp bg-bg-secondary rounded-xl border border-border-primary p-5 hover:border-border-secondary transition-colors" style={{ animationDelay: `${index * 0.08}s` }}>
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-full bg-accent-light flex items-center justify-center shrink-0">
          <span className="text-sm font-semibold text-accent">
            {analyst.name.charAt(0)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-text-primary">
            {analyst.name}
          </h4>
          <div className="flex items-center gap-1.5 mt-0.5">
            <Building2 className="w-3.5 h-3.5 text-text-tertiary" />
            <span className="text-xs text-text-secondary">{analyst.affiliation}</span>
          </div>
          <div className="flex items-start gap-1.5 mt-1.5">
            <Target className="w-3.5 h-3.5 text-text-tertiary mt-0.5 shrink-0" />
            <span className="text-xs text-text-secondary leading-relaxed">{analyst.role}</span>
          </div>
          <p className="text-xs text-text-tertiary mt-2 leading-relaxed">
            {analyst.description}
          </p>
        </div>
      </div>
    </div>
  );
}

export default AnalystCard;