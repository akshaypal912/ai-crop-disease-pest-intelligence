import React from 'react';
import { Info, ShieldCheck, Sprout, Cpu, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const AboutSection: React.FC = () => {
  const supportedCrops = [
    { name: 'Tomato', diseases: 'Late Blight, Early Blight, Yellow Leaf Curl, Septoria' },
    { name: 'Potato', diseases: 'Late Blight, Early Blight, Common Scab' },
    { name: 'Corn / Maize', diseases: 'Common Rust, Northern Leaf Blight, Gray Leaf Spot' },
    { name: 'Apple', diseases: 'Apple Scab, Black Rot, Cedar Apple Rust' },
    { name: 'Cotton', diseases: 'Aphid Vector Infestation, Leaf Curl Virus' },
    { name: 'Wheat & Grains', diseases: 'Leaf Rust, Septoria Tritici, Tan Spot' },
  ];

  return (
    <section id="about" className="py-20 px-4 sm:px-6 lg:px-8 bg-surface-alt bg-organic-texture border-t border-border-soft">
      <div className="max-w-5xl mx-auto space-y-12 text-left">
        
        {/* Section Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#0F3322] text-[#E5C378] text-xs font-extrabold uppercase tracking-wider border border-[#16462D]">
            <Info className="w-3.5 h-3.5 text-[#E5C378]" />
            <span>AI TRANSPARENCY & DECISION SUPPORT</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F3322] tracking-tight">
            About FarmEye AI Platform
          </h2>
          <p className="text-base text-ink-secondary max-w-xl mx-auto font-medium">
            Combining deep neural vision backbones with microclimate telemetry to empower decision support in modern precision agriculture.
          </p>
        </div>

        {/* 2 Column Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Column 1: Core System Architecture */}
          <div className="p-8 rounded-3xl bg-surface-elevated border border-border-soft space-y-4">
            <div className="w-10 h-10 rounded-2xl bg-[#0F3322] text-white flex items-center justify-center border border-[#16462D]">
              <Cpu className="w-5 h-5 text-[#E5C378]" />
            </div>

            <h3 className="text-xl font-extrabold text-[#0F3322]">
              Computer Vision Model Pipeline
            </h3>

            <p className="text-xs text-[#0D1611] leading-relaxed font-semibold">
              FarmEye AI utilizes convolutional backbones trained on over 120,000 expert-curated agricultural leaf specimens. The vision network extracts fine-grained spatial lesion geometries, leaf margin chlorosis, and insect vectors.
            </p>

            <ul className="space-y-2 text-xs text-[#0F3322] font-extrabold pt-2">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                <span>ResNet-50 & MobileNetV3 deep learning architectures</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                <span>Calibrated confidence scoring with uncertainty flags</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                <span>Bounding box localization for pathogen spot clusters</span>
              </li>
            </ul>
          </div>

          {/* Column 2: Decision Support & Trust Principles */}
          <div className="p-8 rounded-3xl bg-surface-elevated border border-border-soft space-y-4">
            <div className="w-10 h-10 rounded-2xl bg-[#0F3322] text-white flex items-center justify-center border border-[#16462D]">
              <ShieldCheck className="w-5 h-5 text-[#10B981]" />
            </div>

            <h3 className="text-xl font-extrabold text-[#0F3322]">
              Ethical AI & Agronomic Reliability
            </h3>

            <p className="text-xs text-[#0D1611] leading-relaxed font-semibold">
              FarmEye AI is strictly positioned as a <strong>decision support platform</strong> to assist farmers and agronomists. It never fabricates certainty when image evidence or weather telemetry is insufficient.
            </p>

            <div className="p-4 rounded-2xl bg-[#F7EFCF] border border-[#D4AF37]/60 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-[#8C6D1F] shrink-0 mt-0.5" />
              <p className="text-xs text-[#8C6D1F] leading-snug font-bold">
                <strong>Important Limitation:</strong> AI visual predictions complement, but do not replace, physical soil testing and pathology laboratory assays for complex viral co-infections.
              </p>
            </div>
          </div>

        </div>

        {/* Supported Crops Grid Table */}
        <div className="p-8 rounded-3xl bg-surface-elevated border border-border-soft space-y-4">
          <div className="flex items-center gap-2 text-xs font-extrabold text-[#0F3322] uppercase tracking-wider">
            <Sprout className="w-4 h-4 text-[#10B981]" />
            <span>Supported Commercial Crop Varieties & Pathogen Classes</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {supportedCrops.map((c) => (
              <div key={c.name} className="p-4 rounded-2xl bg-white border border-border-soft space-y-1">
                <span className="text-xs font-extrabold text-[#0F3322] block">
                  {c.name}
                </span>
                <span className="text-[11px] text-ink-secondary block leading-snug font-semibold">
                  {c.diseases}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};
