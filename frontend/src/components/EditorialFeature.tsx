import React from 'react';
import { IMAGES } from '../data/images';

interface EditorialFeatureProps {
  onDetect: () => void;
}

export const EditorialFeature: React.FC<EditorialFeatureProps> = ({ onDetect }) => {
  return (
    <section className="bg-surface">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-24 lg:py-32 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
        <div className="lg:col-span-5 space-y-6">
          <p className="text-[11px] tracking-[0.28em] uppercase text-olive">
            Crop Disease Intelligence
          </p>
          <h2 className="font-display text-ink text-[42px] sm:text-[56px] leading-[1.05] tracking-[-0.02em]">
            Artificial Intelligence
            <br />
            for Every Field
          </h2>
          <p className="text-ink-muted text-[16px] leading-relaxed max-w-md font-light">
            Photograph a leaf. FarmEye AI locates lesions, estimates severity, and offers practical next steps — keeping agriculture visually first, and intelligence quietly in service of the crop.
          </p>
          <button
            onClick={onDetect}
            className="inline-flex items-center px-6 py-2.5 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm font-semibold hover:bg-[#4F5A38] transition-colors"
          >
            Detect Disease
          </button>
        </div>

        <div className="lg:col-span-7">
          <div className="relative">
            <img
              src={IMAGES.tractorField}
              alt="Tractor working a crop field"
              className="w-full h-[340px] sm:h-[460px] object-cover"
            />
            <div className="absolute -bottom-6 -left-4 sm:-left-8 w-36 h-36 sm:w-44 sm:h-44 rounded-full overflow-hidden ring-8 ring-surface shadow-xl">
              <img src={IMAGES.leaves} alt="Leaf detail" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
