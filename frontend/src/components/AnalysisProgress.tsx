import React from 'react';
import { CheckCircle2, Loader2 } from 'lucide-react';
import { ANALYSIS_STAGES } from '../services/api';
import { IMAGES } from '../data/images';

interface AnalysisProgressProps {
  currentStage: number;
  isOpen: boolean;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ currentStage, isOpen }) => {
  if (!isOpen) return null;

  const progressPercent = Math.min(100, Math.round(((currentStage + 1) / ANALYSIS_STAGES.length) * 100));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#121910]/80">
      <div className="w-full max-w-lg overflow-hidden bg-[#1C2A1A] text-[#F6F1E6] shadow-2xl">
        <img src={IMAGES.leaves} alt="" className="w-full h-32 object-cover opacity-70" />
        <div className="p-7 space-y-6">
          <div>
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3] mb-2">FarmEye AI</p>
            <h3 className="font-display text-3xl">Listening to the leaf…</h3>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-[#E8D5A3]">{progressPercent}%</span>
            </div>
            <div className="h-[3px] bg-white/15">
              <div className="h-full bg-[#E8D5A3] transition-all" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>

          <div className="space-y-3">
            {ANALYSIS_STAGES.map((stageItem, index) => {
              const isCompleted = index < currentStage;
              const isCurrent = index === currentStage;
              return (
                <div key={stageItem.stage} className="flex gap-3 items-start">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-[#E8D5A3] mt-0.5" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-[#E8D5A3] animate-spin mt-0.5" />
                  ) : (
                    <span className="w-4 h-4 mt-0.5 rounded-full border border-white/25" />
                  )}
                  <div>
                    <p className={`text-sm ${isCurrent ? 'text-[#E8D5A3]' : 'text-white/85'}`}>{stageItem.title}</p>
                    <p className="text-xs text-white/50 font-light">{stageItem.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
