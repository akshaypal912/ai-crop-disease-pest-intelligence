import React from 'react';
import { AlertOctagon } from 'lucide-react';
import type { DiseaseDiagnosis } from '../types/crop';

export const DiagnosisCard: React.FC<{ diagnosis: DiseaseDiagnosis }> = ({ diagnosis }) => {
  const isUncertain = !diagnosis.isReliable || diagnosis.confidence < 60;

  return (
    <article className="border-t border-border pt-8 space-y-6">
      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">Primary diagnosis</p>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-4xl text-ink leading-tight">{diagnosis.diseaseName}</h2>
          {diagnosis.scientificName && (
            <p className="mt-1 italic text-ink-muted">{diagnosis.scientificName}</p>
          )}
        </div>
        <span className="text-xs uppercase tracking-widest text-olive">{diagnosis.severity}</span>
      </div>

      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-ink-muted">Model confidence</span>
          <span className="font-display text-2xl">{diagnosis.confidence.toFixed(1)}%</span>
        </div>
        <div className="h-[3px] bg-[#DDD6C4]">
          <div className="h-full bg-[#6E7A4E]" style={{ width: `${Math.max(8, diagnosis.confidence)}%` }} />
        </div>
      </div>

      <p className="text-ink-muted font-light leading-relaxed">{diagnosis.summary}</p>

      {isUncertain && (
        <div className="flex gap-3 bg-surface-soft p-4">
          <AlertOctagon className="w-5 h-5 text-[#8A3E38] shrink-0" />
          <p className="text-sm text-ink-muted font-light">
            Confidence is below 60%. Confirm symptoms in the field, or recapture the leaf in even daylight.
          </p>
        </div>
      )}
    </article>
  );
};
