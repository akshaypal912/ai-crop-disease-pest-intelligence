import React, { useEffect } from 'react';
import { ArrowLeft, Check, Leaf } from 'lucide-react';
import type { DiseaseLibraryEntry } from '../../types/diseaseLibrary';

interface DiseaseDetailPageProps {
  disease: DiseaseLibraryEntry;
  onBack: () => void;
  onAnalyze: () => void;
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="border-t border-border pt-8 space-y-4">
      <h2 className="text-[11px] tracking-[0.28em] uppercase text-olive">{title}</h2>
      {children}
    </section>
  );
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="space-y-2 text-sm text-ink-secondary leading-relaxed font-light">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <span className="text-olive mt-1.5 shrink-0">•</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function CheckList({ items }: { items: string[] }) {
  return (
    <ul className="space-y-2 text-sm text-ink-secondary leading-relaxed font-light">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <Check className="w-4 h-4 text-olive mt-0.5 shrink-0" aria-hidden />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export const DiseaseDetailPage: React.FC<DiseaseDetailPageProps> = ({
  disease,
  onBack,
  onAnalyze,
}) => {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = `${disease.name} | FarmEye AI`;
    const meta = document.querySelector('meta[name="description"]');
    const previousDescription = meta?.getAttribute('content') ?? '';
    meta?.setAttribute('content', disease.metaDescription);

    return () => {
      document.title = previousTitle;
      meta?.setAttribute('content', previousDescription);
    };
  }, [disease]);

  return (
    <main className="bg-surface min-h-screen pb-20">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 pt-28">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 text-sm text-ink-muted hover:text-ink-strong transition-colors mb-8"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden />
          Back to Disease Library
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14">
          <div className="lg:col-span-5">
            <div className="overflow-hidden rounded-lg shadow-lg ring-1 ring-[#DDD6C4]/80">
              <img
                src={disease.image}
                alt={disease.name}
                className="w-full aspect-[4/3] object-cover"
              />
            </div>
          </div>

          <div className="lg:col-span-7 space-y-4">
            <p className="text-[11px] tracking-[0.28em] uppercase text-olive">
              Educational information
            </p>
            <h1 className="font-display text-4xl sm:text-5xl text-ink leading-tight">
              {disease.name}
            </h1>
            <p className="text-sm text-ink-muted font-medium">
              {disease.crop} • {disease.category}
            </p>
            <p className="text-base text-ink-secondary leading-relaxed font-light max-w-2xl">
              {disease.shortDescription}
            </p>
          </div>
        </div>

        <div className="mt-14 max-w-3xl space-y-0">
          <Section title="Overview">
            <h3 className="font-display text-2xl text-ink">What is it?</h3>
            <p className="text-sm text-ink-secondary leading-relaxed font-light">{disease.overview}</p>
          </Section>

          <Section title="Symptoms">
            <BulletList items={disease.symptoms} />
          </Section>

          <Section title="Causes">
            <BulletList items={disease.causes} />
          </Section>

          <Section title="Favorable conditions">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { label: 'Temperature', value: disease.favorableConditions.temperature },
                { label: 'Humidity', value: disease.favorableConditions.humidity },
                { label: 'Moisture', value: disease.favorableConditions.moisture },
              ].map((item) => (
                <div
                  key={item.label}
                  className="p-4 rounded-2xl bg-surface-elevated border border-border text-sm"
                >
                  <p className="text-[11px] uppercase tracking-wider text-olive mb-1">
                    {item.label}
                  </p>
                  <p className="text-ink-secondary font-light leading-relaxed">{item.value}</p>
                </div>
              ))}
            </div>
            {disease.favorableConditions.other.length > 0 && (
              <div className="pt-2">
                <p className="text-xs uppercase tracking-wider text-olive mb-2">Other factors</p>
                <BulletList items={disease.favorableConditions.other} />
              </div>
            )}
          </Section>

          <Section title="Severity">
            <p className="font-display text-2xl text-ink">{disease.severity}</p>
            <p className="text-sm text-ink-secondary leading-relaxed font-light">
              {disease.severityExplanation}
            </p>
          </Section>

          <Section title="Prevention">
            <CheckList items={disease.prevention} />
          </Section>

          <Section title="Management">
            <p className="text-xs text-ink-muted font-light mb-3">
              General practices only. Follow your local agricultural authority and product labels for
              any chemical control.
            </p>
            <BulletList items={disease.management} />
          </Section>

          <Section title="When to act">
            <p className="text-sm text-ink-secondary leading-relaxed font-light">{disease.whenToAct}</p>
          </Section>

          <Section title="FarmEye AI detection">
            <div className="p-6 rounded-2xl bg-[#1C2A1A] text-[#F6F1E6] space-y-4">
              <div className="flex items-center gap-2 text-[#E8D5A3]">
                <Leaf className="w-5 h-5" aria-hidden />
                <span className="text-sm font-semibold">Decision support — not a confirmed diagnosis</span>
              </div>
              <p className="text-sm text-white/85 font-light leading-relaxed">
                Upload a clear image of the affected leaf to let FarmEye AI analyze visible symptoms
                and highlight areas worth scouting. {disease.detectionNotes}
              </p>
              <button
                type="button"
                onClick={onAnalyze}
                className="inline-flex items-center px-6 py-3 rounded-full bg-[#E8D5A3] text-ink-strong text-sm font-semibold hover:bg-white transition-colors"
              >
                Analyze My Crop
              </button>
            </div>
          </Section>
        </div>
      </div>
    </main>
  );
};
