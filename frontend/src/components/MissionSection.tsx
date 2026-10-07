import React from 'react';

interface MissionSectionProps {
  onDetect: () => void;
}

export const MissionSection: React.FC<MissionSectionProps> = ({ onDetect }) => {
  return (
    <section id="explore" className="relative bg-[#6E7A4E] text-[#F6F1E6] overflow-hidden">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-24 lg:py-32">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-20 items-start">
          <div className="lg:col-span-7 space-y-5">
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3]">
              Field Intelligence
            </p>
            <h2 className="font-display text-[42px] sm:text-[58px] lg:text-[68px] leading-[1.02] tracking-[-0.02em]">
              Smarter Farming.
              <br />
              Healthier Crops.
              <br />
              A Better Future.
            </h2>
          </div>

          <div className="lg:col-span-5 lg:pt-10 space-y-8">
            <p className="text-[#F6F1E6]/88 text-[16px] leading-relaxed font-light">
              CropSense reads the subtle language of leaves, canopies and soil. We pair realistic field observation with careful AI analysis so growers can act earlier — with clarity, not guesswork.
            </p>
            <button
              onClick={onDetect}
              className="inline-flex items-center px-6 py-2.5 rounded-full bg-[#E8D5A3] text-[#1C2A1A] text-sm font-semibold hover:bg-white transition-colors"
            >
              Begin a Field Scan
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
