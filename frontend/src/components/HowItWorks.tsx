import React from 'react';
import { Upload, Cpu, CheckCircle2, ArrowRight } from 'lucide-react';

interface HowItWorksProps {
  onAnalyzeClick: () => void;
}

export const HowItWorks: React.FC<HowItWorksProps> = ({ onAnalyzeClick }) => {
  const steps = [
    {
      step: '01',
      title: 'Upload Crop Image',
      description: 'Upload a clear leaf or canopy photograph or capture one directly from your field smartphone camera.',
      icon: Upload,
      accent: 'border-[#0F3322]/40 bg-[#E3ECE5] text-[#0F3322]',
    },
    {
      step: '02',
      title: 'AI Analyzes the Crop',
      description: 'Computer vision neural networks scan cellular leaf patterns, bounding lesion zones and identifying pest vectors.',
      icon: Cpu,
      accent: 'border-[#D4AF37]/50 bg-[#F7EFCF] text-[#8C6D1F]',
    },
    {
      step: '03',
      title: 'Understand & Act',
      description: 'Review diagnostic confidence, severity assessments, weather risk matrix, and actionable treatment steps.',
      icon: CheckCircle2,
      accent: 'border-[#10B981]/40 bg-emerald-100 text-emerald-900',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8 bg-[#FAF8F3] bg-leaf-pattern border-y border-[#CFDAD2] relative overflow-hidden">
      <div className="max-w-7xl mx-auto text-center space-y-12">
        
        {/* Section Header */}
        <div className="space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#E3ECE5] text-[#0F3322] text-xs font-extrabold uppercase tracking-wider border border-[#CFDAD2]">
            3-STEP INTELLIGENCE WORKFLOW
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F3322] tracking-tight">
            How CropSense AI Works
          </h2>
          <p className="text-base text-[#43544A] font-medium">
            From raw leaf image to precise agronomic guidance in seconds. Designed for farmers, agronomists, and crop researchers.
          </p>
        </div>

        {/* 3 Step Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left relative">
          {steps.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="group relative p-8 rounded-3xl bg-[#F6F3EC] border border-[#CFDAD2] hover:border-[#0F3322] transition-all duration-300 hover:shadow-xl hover:-translate-y-1 flex flex-col justify-between"
              >
                <div>
                  {/* Step Number & Icon Header */}
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-4xl font-extrabold text-[#0F3322]/25 tracking-tighter group-hover:text-[#0F3322] transition-colors">
                      {item.step}
                    </span>
                    <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center shadow-sm ${item.accent}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-xl font-extrabold text-[#0F3322] mb-3 group-hover:text-[#0F3322] transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-sm text-[#43544A] leading-relaxed font-medium">
                    {item.description}
                  </p>
                </div>

                {/* Bottom Connector indicator */}
                <div className="pt-6 mt-6 border-t border-[#CFDAD2] flex items-center justify-between text-xs font-extrabold text-[#0F3322]">
                  <span>Step {index + 1} of 3</span>
                  <ArrowRight className="w-4 h-4 text-[#10B981] transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA Banner */}
        <div className="pt-4">
          <button
            onClick={onAnalyzeClick}
            className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-[#0F3322] text-white text-xs font-extrabold hover:bg-[#16462D] transition-all shadow-md border border-[#16462D]"
          >
            <span>Start Image Scan</span>
            <ArrowRight className="w-4 h-4 text-[#E5C378]" />
          </button>
        </div>

      </div>
    </section>
  );
};
