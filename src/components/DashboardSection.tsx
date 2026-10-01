import React from 'react';
import type { Alert, AnalysisResult } from '../types/crop';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';

interface DashboardSectionProps {
  historyItems: AnalysisResult[];
  alerts: Alert[];
  onDetect: () => void;
  onOpenResult: (item: AnalysisResult) => void;
}

export const DashboardSection: React.FC<DashboardSectionProps> = ({
  historyItems,
  alerts,
  onDetect,
  onOpenResult,
}) => {
  const latest = historyItems[0];
  const healthy = historyItems.filter((h) => h.diagnosis.severity === 'healthy').length;

  return (
    <div className="bg-[#FBF7EE] min-h-screen">
      <PageBanner
        kicker="Dashboard"
        title="The season, at a glance"
        subtitle="Field alerts, recent readings and crop health — presented as a working farm brief, not a software console."
        image={IMAGES.farmland}
      />

      <section className="bg-[#6E7A4E] text-[#F6F1E6]">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 grid grid-cols-1 md:grid-cols-3 gap-10">
          <Stat label="Readings" value={String(historyItems.length)} note="Stored field scans" />
          <Stat label="Healthy" value={String(healthy)} note="Crops without active disease" />
          <Stat label="Alerts" value={String(alerts.length)} note="Open field warnings" />
        </div>
      </section>

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-20 grid grid-cols-1 lg:grid-cols-12 gap-16">
        <div className="lg:col-span-7 space-y-8">
          <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">Field warnings</p>
          <h2 className="font-display text-4xl sm:text-5xl text-[#161A12] leading-tight">
            What the land
            <br />
            is asking for
          </h2>

          {alerts.length === 0 ? (
            <p className="text-[#5A6150] font-light max-w-md">
              No outbreak warnings right now. Keep scanning through weather shifts and dense canopy weeks.
            </p>
          ) : (
            <div className="space-y-8">
              {alerts.map((alt) => (
                <div key={alt.id} className="border-t border-[#DDD6C4] pt-6">
                  <p className="text-[11px] tracking-[0.2em] uppercase text-[#6E7A4E] mb-2">
                    {alt.severity} · {alt.cropType || 'Field'} · {alt.timestamp}
                  </p>
                  <h3 className="font-display text-2xl text-[#161A12] mb-2">{alt.reason}</h3>
                  <p className="text-[#5A6150] font-light">{alt.action}</p>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={onDetect}
            className="px-6 py-2.5 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm"
          >
            Detect Disease
          </button>
        </div>

        <div className="lg:col-span-5">
          <div className="relative">
            <img src={IMAGES.healthyCrops} alt="Crop rows" className="w-full h-72 object-cover" />
            <div className="absolute -bottom-8 -left-4 w-32 h-32 rounded-full overflow-hidden ring-8 ring-[#FBF7EE]">
              <img src={IMAGES.corn} alt="" className="w-full h-full object-cover" />
            </div>
          </div>

          {latest && (
            <div className="mt-16">
              <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E] mb-3">Latest reading</p>
              <h3 className="font-display text-3xl text-[#161A12] mb-3">{latest.diagnosis.diseaseName}</h3>
              <p className="text-sm text-[#5A6150] font-light mb-5">{latest.diagnosis.summary}</p>
              <button
                onClick={() => onOpenResult(latest)}
                className="text-sm border-b border-[#1C2A1A] pb-0.5"
              >
                Open full result
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function Stat({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div>
      <p className="text-[11px] tracking-[0.24em] uppercase text-[#E8D5A3] mb-2">{label}</p>
      <p className="font-display text-6xl leading-none">{value}</p>
      <p className="mt-3 text-white/75 font-light text-sm">{note}</p>
    </div>
  );
}
