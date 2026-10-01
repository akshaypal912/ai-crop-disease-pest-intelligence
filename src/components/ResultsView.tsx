import React from 'react';
import { ArrowLeft, Printer } from 'lucide-react';
import type { AnalysisResult } from '../types/crop';
import { DetectionOverlay } from './DetectionOverlay';
import { DiagnosisCard } from './DiagnosisCard';
import { PestDetectionCard } from './PestDetectionCard';
import { RiskCard } from './RiskCard';
import { RecommendationsCard } from './RecommendationsCard';
import { IMAGES } from '../data/images';

interface ResultsViewProps {
  result: AnalysisResult;
  onBack: () => void;
  onAnalyzeAnother: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  result,
  onBack,
  onAnalyzeAnother
}) => {
  return (
    <div className="bg-[#FBF7EE] min-h-screen">
      <section className="relative overflow-hidden min-h-[38vh]">
        <img src={IMAGES.sunsetFarm} alt="" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(18,25,16,0.78)_0%,rgba(18,25,16,0.4)_100%)]" />
        <div className="relative z-10 max-w-[1400px] mx-auto px-6 sm:px-10 pt-28 pb-12">
          <button onClick={onBack} className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[#E8D5A3] mb-6">
            <ArrowLeft className="w-4 h-4" /> Return to detect
          </button>
          <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3] mb-3">Result · {result.id}</p>
          <h1 className="font-display text-[#F4E7C0] text-[42px] sm:text-[62px] leading-[0.98] max-w-4xl">
            {result.diagnosis.diseaseName}
          </h1>
          <p className="mt-4 text-white/75 max-w-xl font-light">
            {result.cropType} · {result.location || 'Unspecified plot'} · {new Date(result.timestamp).toLocaleString()}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button
              onClick={onAnalyzeAnother}
              className="px-6 py-2.5 rounded-full bg-[#E8D5A3] text-[#1C2A1A] text-sm font-semibold"
            >
              Detect another crop
            </button>
            <button
              onClick={() => window.print()}
              className="px-6 py-2.5 rounded-full border border-white/30 text-white text-sm inline-flex items-center gap-2"
            >
              <Printer className="w-4 h-4" /> Print reading
            </button>
          </div>
        </div>
      </section>

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div className="lg:col-span-5 space-y-6">
          <DetectionOverlay
            imageUrl={result.imageUrl}
            boundingBoxes={result.diagnosis.boundingBoxes}
            pestBoxes={result.pests.boundingBoxes}
          />
          <p className="text-sm text-[#5A6150] font-light leading-relaxed">
            Highlighted regions mark lesions or pest activity. The photograph remains the primary evidence; the model only annotates what it can see.
          </p>
        </div>
        <div className="lg:col-span-7 space-y-6">
          <DiagnosisCard diagnosis={result.diagnosis} />
          <PestDetectionCard pests={result.pests} />
          <RiskCard environment={result.environment} risk={result.risk} />
          <RecommendationsCard recommendations={result.recommendations} />
        </div>
      </div>
    </div>
  );
};
