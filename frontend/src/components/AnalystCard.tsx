import { Building2, Target } from 'lucide-react';
import type { Analyst } from '../types';

interface AnalystCardProps {
  analyst: Analyst;
  index: number;
}

function AnalystCard({ analyst, index }: AnalystCardProps) {
  return (
    <div className="animate-slideUp gemini-card p-5 hover:border-border-secondary hover:shadow-md hover:-translate-y-0.5" style={{ animationDelay: `${index * 0.08}s` }}>
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#4285f4] via-[#9b51e0] to-[#e91e63] p-[2px] flex items-center justify-center shrink-0">
          <div className="w-full h-full rounded-full bg-bg-secondary flex items-center justify-center">
            <span className="text-sm font-bold bg-gradient-to-r from-[#4285f4] to-[#9b51e0] bg-clip-text text-transparent">
              {analyst.name.charAt(0)}
            </span>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-bold text-text-primary">
            {analyst.name}
          </h4>
          <div className="flex items-center gap-1.5 mt-0.5">
            <Building2 className="w-3.5 h-3.5 text-text-tertiary" />
            <span className="text-xs font-medium text-text-secondary">{analyst.affiliation}</span>
          </div>
          <div className="flex items-start gap-1.5 mt-1.5">
            <Target className="w-3.5 h-3.5 text-text-tertiary mt-0.5 shrink-0" />
            <span className="text-xs text-text-secondary leading-relaxed font-medium">{analyst.role}</span>
          </div>
          <p className="text-xs text-text-tertiary mt-2.5 leading-relaxed">
            {analyst.description}
          </p>
        </div>
      </div>
    </div>
  );
}

export default AnalystCard;