import React from 'react';
import type { DiseaseLibraryEntry } from '../../types/diseaseLibrary';

interface DiseaseCardProps {
  disease: DiseaseLibraryEntry;
  onOpen: (slug: string) => void;
}

export const DiseaseCard: React.FC<DiseaseCardProps> = ({ disease, onOpen }) => {
  return (
    <button
      type="button"
      onClick={() => onOpen(disease.id)}
      className="text-left group w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1C2A1A] focus-visible:ring-offset-4 focus-visible:ring-offset-surface rounded-sm"
      aria-label={`View details for ${disease.name}`}
    >
      <div className="relative h-36 overflow-hidden">
        <img
          src={disease.image}
          alt={disease.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
        />
      </div>
      <span className="mt-2 block font-display text-ink">{disease.name}</span>
      <p className="mt-1 text-xs text-ink-muted font-light line-clamp-2 leading-relaxed">
        {disease.shortDescription}
      </p>
      <span className="mt-2 inline-block text-xs font-medium text-olive group-hover:text-ink-strong transition-colors">
        View Details →
      </span>
    </button>
  );
};
