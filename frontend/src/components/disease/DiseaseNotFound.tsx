import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface DiseaseNotFoundProps {
  onBack: () => void;
}

export const DiseaseNotFound: React.FC<DiseaseNotFoundProps> = ({ onBack }) => {
  return (
    <main className="bg-surface min-h-screen px-6 sm:px-10 pt-28 pb-20">
      <div className="max-w-lg mx-auto text-center space-y-6">
        <h1 className="font-display text-3xl text-ink">Condition not found</h1>
        <p className="text-ink-muted font-light">
          We could not find educational information for this link. Return to the disease library on
          the detect page.
        </p>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Disease Library
        </button>
      </div>
    </main>
  );
};
