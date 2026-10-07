import React from 'react';

interface PageBannerProps {
  kicker: string;
  title: string;
  subtitle: string;
  image: string;
}

export const PageBanner: React.FC<PageBannerProps> = ({ kicker, title, subtitle, image }) => {
  return (
    <section className="relative h-[42vh] min-h-[320px] overflow-hidden">
      <img src={image} alt="" className="absolute inset-0 w-full h-full object-cover" />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(18,25,16,0.72)_0%,rgba(18,25,16,0.35)_100%)]" />
      <div className="relative z-10 h-full max-w-[1400px] mx-auto px-6 sm:px-10 flex flex-col justify-end pb-12 pt-28">
        <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3] mb-3">{kicker}</p>
        <h1 className="font-display text-[#F4E7C0] text-[40px] sm:text-[58px] leading-[0.98] max-w-3xl">
          {title}
        </h1>
        <p className="mt-4 text-white/80 max-w-xl text-[15px] font-light">{subtitle}</p>
      </div>
    </section>
  );
};
