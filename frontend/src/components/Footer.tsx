import React from 'react';
import { Leaf } from 'lucide-react';
import type { AppPage } from './Navbar';

interface FooterProps {
  onNavigate: (page: AppPage) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-[#1C2A1A] text-[#F6F1E6]">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 grid grid-cols-1 md:grid-cols-12 gap-10">
        <div className="md:col-span-6 space-y-4">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-[#E8D5A3]" />
            <span className="font-display text-2xl">CropSense</span>
          </div>
          <p className="text-white/70 text-sm font-light max-w-md leading-relaxed">
            Agricultural intelligence for growers who still believe the field should look like a field — even on a screen.
          </p>
        </div>
        <div className="md:col-span-3 space-y-3">
          <p className="text-[11px] tracking-[0.22em] uppercase text-[#E8D5A3]">Visit</p>
          {([
            ['home', 'Home'],
            ['detect', 'Detect'],
            ['history', 'History'],
            ['dashboard', 'Dashboard'],
          ] as const).map(([id, label]) => (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className="block text-sm text-white/75 hover:text-[#E8D5A3]"
            >
              {label}
            </button>
          ))}
        </div>
        <div className="md:col-span-3 space-y-3">
          <p className="text-[11px] tracking-[0.22em] uppercase text-[#E8D5A3]">Note</p>
          <p className="text-sm text-white/70 font-light leading-relaxed">
            CropSense is a decision-support tool. Pair every scan with on-farm observation.
          </p>
        </div>
      </div>
      <div className="border-t border-white/10 px-6 sm:px-10 py-6 text-xs text-white/50 flex flex-col sm:flex-row justify-between gap-2 max-w-[1400px] mx-auto">
        <span>© {new Date().getFullYear()} CropSense</span>
        <span>Agriculture first. Intelligence second.</span>
      </div>
    </footer>
  );
};
