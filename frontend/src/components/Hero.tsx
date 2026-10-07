import React from 'react';
import { IMAGES } from '../data/images';

const HERO_VIDEO_EMBED_SRC =
  'https://www.youtube.com/embed/cBMg2-qBVeM?start=31&rel=0&modestbranding=1';

interface HeroProps {
  onDetect: () => void;
  onExplore: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onDetect, onExplore }) => {
  return (
    <section className="relative min-h-screen w-full overflow-hidden">
      <img
        src={IMAGES.heroField}
        alt="Golden crop field at harvest"
        className="absolute inset-0 w-full h-full object-cover object-center"
      />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(18,25,16,0.62)_0%,rgba(18,25,16,0.28)_48%,rgba(18,25,16,0.45)_100%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(18,25,16,0.35)_0%,transparent_28%,rgba(18,25,16,0.45)_100%)]" />

      <div className="relative z-10 min-h-screen max-w-[1400px] mx-auto px-6 sm:px-10 pt-28 pb-16 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end lg:items-center flex-1">
          <div className="lg:col-span-8">
            <h1 className="font-display text-[#F4E7C0] text-[56px] sm:text-[80px] lg:text-[108px] leading-[0.92] tracking-[-0.03em] max-w-4xl">
              See Your Crop.
              <br />
              Understand Its
              <br />
              Health.
            </h1>
          </div>

          <div className="lg:col-span-4 lg:justify-self-end lg:text-right max-w-sm lg:ml-auto space-y-6">
            <p className="text-white/85 text-[15px] sm:text-base leading-relaxed font-light">
              FarmEye AI uses computer vision and intelligent risk analysis to help identify crop diseases and pests early.
            </p>
            <div className="flex flex-wrap gap-3 lg:justify-end">
              <button
                onClick={onDetect}
                className="px-6 py-2.5 rounded-full bg-[#F4E7C0] text-ink-strong text-sm font-semibold hover:bg-white transition-colors"
              >
                Detect Disease
              </button>
              <button
                onClick={onExplore}
                className="px-6 py-2.5 rounded-full border border-white/40 text-white text-sm font-medium hover:bg-white/10 transition-colors"
              >
                Explore FarmEye
              </button>
            </div>
          </div>
        </div>

        <div className="mt-16 lg:mt-20 flex flex-col sm:flex-row sm:items-end justify-between gap-8">
          <div className="flex items-center gap-4 text-white/70 text-xs tracking-[0.18em] uppercase">
            <span className="w-10 h-px bg-white/40" />
            Field intelligence since harvest
          </div>

          <div className="relative w-full max-w-[220px] sm:max-w-[260px] aspect-video rounded-lg overflow-hidden shadow-2xl ring-1 ring-white/20 animate-float self-end">
            <iframe
              src={HERO_VIDEO_EMBED_SRC}
              title="From field to diagnosis"
              className="absolute inset-0 w-full h-full border-0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
            <p className="absolute bottom-2 left-3 right-3 text-[10px] tracking-[0.12em] uppercase text-white/90 pointer-events-none drop-shadow-sm">
              From field to diagnosis
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
