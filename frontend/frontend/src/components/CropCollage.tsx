import React from 'react';
import { IMAGES } from '../data/images';

export const CropCollage: React.FC = () => {
  return (
    <section className="relative bg-[#5F6A42] overflow-hidden py-8 lg:py-4">
      <p className="absolute left-0 top-6 lg:top-10 font-display text-[72px] sm:text-[110px] lg:text-[150px] leading-none text-[#4A5434]/80 whitespace-nowrap px-4 pointer-events-none select-none">
        From Seed to Harvest
      </p>

      <div className="relative max-w-[1400px] mx-auto px-4 sm:px-8 pt-24 pb-16 lg:pt-32 lg:pb-20 min-h-[520px] lg:min-h-[640px]">
        <CirclePhoto src={IMAGES.wheat} alt="Wheat" className="w-40 h-40 sm:w-52 sm:h-52 left-[2%] top-[18%] z-20" />
        <CirclePhoto src={IMAGES.tomato} alt="Tomato" className="w-24 h-24 sm:w-32 sm:h-32 left-[22%] top-[8%] z-10" />
        <CirclePhoto src={IMAGES.corn} alt="Corn" className="w-36 h-36 sm:w-48 sm:h-48 left-[18%] bottom-[8%] z-30" />
        <CirclePhoto src={IMAGES.soilHands} alt="Harvest in hands" className="w-28 h-28 sm:w-36 sm:h-36 left-[38%] top-[28%] z-20" />
        <CirclePhoto src={IMAGES.healthyCrops} alt="Healthy crops" className="w-44 h-44 sm:w-64 sm:h-64 left-[46%] bottom-[4%] z-20" />
        <CirclePhoto src={IMAGES.leaves} alt="Green leaves" className="w-28 h-28 sm:w-40 sm:h-40 right-[26%] top-[10%] z-10" />
        <CirclePhoto src={IMAGES.farmland} alt="Farmland" className="hidden sm:block w-36 h-36 right-[8%] top-[18%] z-20" />
        <CirclePhoto src={IMAGES.apple} alt="Apple" className="w-24 h-24 sm:w-28 sm:h-28 right-[18%] bottom-[18%] z-30" />
        <CirclePhoto src={IMAGES.rice} alt="Rice" className="w-32 h-32 sm:w-44 sm:h-44 right-[2%] bottom-[6%] z-20" />
      </div>
    </section>
  );
};

function CirclePhoto({
  src,
  alt,
  className,
}: {
  src: string;
  alt: string;
  className: string;
}) {
  return (
    <div className={`absolute rounded-full overflow-hidden shadow-[0_18px_40px_rgba(18,25,16,0.28)] ring-4 ring-[#F6F1E6]/15 ${className}`}>
      <img src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
}
