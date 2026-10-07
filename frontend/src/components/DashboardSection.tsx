import React from 'react';
import type { CropAnalysisSession } from '../types/session';
import { sessionDiagnosisTitle } from '../types/session';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';

interface DashboardSectionProps {
  historyItems: CropAnalysisSession[];
  onDetect: () => void;
  onOpenResult: (item: CropAnalysisSession) => void;
}

export const DashboardSection: React.FC<DashboardSectionProps> = ({
  historyItems,
  onDetect,
  onOpenResult,
}) => {
  const latest = historyItems[0];
  const alertCount = historyItems.filter((h) => h.report.alert.active).length;
  const tomatoRuns = historyItems.filter(
    (h) => h.report.specialist_routing.routing_status === 'TOMATO_SPECIALIST'
  ).length;

  return (
    <div className="bg-surface min-h-screen">
      <PageBanner
        kicker="Dashboard"
        title="The season, at a glance"
        subtitle="FarmEye AI summaries from live backend analyses in this browser."
        image={IMAGES.farmland}
      />

      <section className="bg-[#6E7A4E] text-[#F6F1E6]">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 grid grid-cols-1 md:grid-cols-3 gap-10">
          <Stat label="Readings" value={String(historyItems.length)} note="Stored analyses" />
          <Stat label="Tomato specialist runs" value={String(tomatoRuns)} note="Validated routing" />
          <Stat label="Active alerts" value={String(alertCount)} note="From backend alert field" />
        </div>
      </section>

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-20">
        {latest ? (
          <button
            type="button"
            onClick={() => onOpenResult(latest)}
            className="text-left border-t border-border pt-8 w-full"
          >
            <p className="text-[11px] tracking-[0.28em] uppercase text-olive">Latest reading</p>
            <h2 className="font-display text-4xl text-ink mt-2">{sessionDiagnosisTitle(latest)}</h2>
          </button>
        ) : (
          <p className="text-ink-muted font-light">No analyses yet.</p>
        )}
        <button
          type="button"
          onClick={onDetect}
          className="mt-10 px-6 py-3 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm"
        >
          New detection
        </button>
      </div>
    </div>
  );
};

function Stat({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div>
      <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3]">{label}</p>
      <p className="font-display text-5xl mt-2">{value}</p>
      <p className="text-sm text-[#E8D5A3]/80 mt-1">{note}</p>
    </div>
  );
}
