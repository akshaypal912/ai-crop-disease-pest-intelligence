import React from 'react';
import { Target, ShieldCheck, Thermometer, AlertTriangle, Bug, FileSpreadsheet, Bell, Crosshair } from 'lucide-react';

export const Capabilities: React.FC = () => {
  const capabilities = [
    {
      title: 'Pathogen & Disease Identification',
      description: 'Accurately classifies fungal, bacterial, and viral crop diseases across major commercial crop varieties.',
      icon: Target,
      tag: 'Computer Vision'
    },
    {
      title: 'Calibrated Confidence Scoring',
      description: 'Outputs honest diagnostic probability scores and flags low-confidence images for manual agronomic verification.',
      icon: ShieldCheck,
      tag: 'AI Reliability'
    },
    {
      title: 'Lesion & Symptom Bounding Overlay',
      description: 'Generates bounding box coordinates highlighting chlorotic halos, pustules, and necrotizing leaf spots.',
      icon: Crosshair,
      tag: 'Visual Bounding'
    },
    {
      title: 'Pest Vector Localization',
      description: 'Detects sucking insects, aphids, spider mites, and caterpillar feeding signs with counts and confidence.',
      icon: Bug,
      tag: 'Entomology AI'
    },
    {
      title: 'Environmental Microclimate Integration',
      description: 'Pairs leaf diagnosis with ambient temperature, humidity, rainfall, and leaf wetness hours.',
      icon: Thermometer,
      tag: 'AgWeather API'
    },
    {
      title: 'Explainable Risk Assessment',
      description: 'Explains underlying infection drivers rather than giving arbitrary black-box risk numbers.',
      icon: AlertTriangle,
      tag: 'Explainable AI'
    },
    {
      title: 'Actionable Field Guidance',
      description: 'Provides practical step-by-step treatment categorised into Monitor, Field Care, and Follow-up.',
      icon: FileSpreadsheet,
      tag: 'Agronomy Rules'
    },
    {
      title: 'Automated Field Alerting',
      description: 'Triggers prioritized field warnings when weather and pathogen conditions reach outbreak thresholds.',
      icon: Bell,
      tag: 'Outbreak Prevention'
    }
  ];

  return (
    <section id="capabilities" className="py-20 px-4 sm:px-6 lg:px-8 bg-surface-alt bg-organic-texture border-b border-border-soft">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Section Header */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#0F3322] text-[#E5C378] text-xs font-extrabold uppercase tracking-wider border border-[#16462D]">
            PLATFORM CAPABILITIES
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F3322] tracking-tight">
            Built for Precision Agronomy & Reliable AI
          </h2>
          <p className="text-base text-ink-secondary font-medium">
            Every feature is grounded in explainable machine learning and agricultural best practices. No black-box scores or fabricated predictions.
          </p>
        </div>

        {/* Capabilities Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <div
                key={cap.title}
                className="p-6 rounded-2xl bg-white border border-border-soft hover:border-[#0F3322] hover:shadow-xl transition-all duration-300 flex flex-col justify-between group"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-[#0F3322] text-[#10B981] flex items-center justify-center group-hover:bg-[#16462D] group-hover:text-[#E5C378] transition-colors border border-[#16462D]">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-surface-elevated text-[#0F3322] border border-border-soft">
                      {cap.tag}
                    </span>
                  </div>

                  <h3 className="text-base font-extrabold text-[#0F3322] leading-snug">
                    {cap.title}
                  </h3>
                  <p className="text-xs text-ink-secondary leading-relaxed font-medium">
                    {cap.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
