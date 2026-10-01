import React, { useState } from 'react';
import { Search, Trash2, Calendar, MapPin } from 'lucide-react';
import type { AnalysisResult } from '../types/crop';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';

interface HistorySectionProps {
  historyItems: AnalysisResult[];
  onSelectResult: (result: AnalysisResult) => void;
  onClearHistory: () => void;
  onDeleteItem: (id: string) => void;
}

export const HistorySection: React.FC<HistorySectionProps> = ({
  historyItems = [],
  onSelectResult,
  onClearHistory,
  onDeleteItem
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCropFilter, setSelectedCropFilter] = useState('all');

  const filteredItems = historyItems.filter((item) => {
    const matchesSearch =
      item.diagnosis.diseaseName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.cropType.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.location && item.location.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCrop = selectedCropFilter === 'all' || item.cropType === selectedCropFilter;
    return matchesSearch && matchesCrop;
  });

  const uniqueCrops = Array.from(new Set(historyItems.map((h) => h.cropType)));

  return (
    <div className="bg-[#FBF7EE] min-h-screen">
      <PageBanner
        kicker="History"
        title="A ledger of every field reading"
        subtitle="Revisit past diagnoses, compare seasons, and keep a living archive of crop health."
        image={IMAGES.wheat}
      />

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 space-y-10">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
          <div>
            <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E] mb-2">Archive</p>
            <h2 className="font-display text-4xl text-[#161A12]">{historyItems.length} recorded scans</h2>
          </div>
          {historyItems.length > 0 && (
            <button onClick={onClearHistory} className="inline-flex items-center gap-2 text-sm text-[#8A3E38]">
              <Trash2 className="w-4 h-4" /> Clear archive
            </button>
          )}
        </div>

        <div className="flex flex-col sm:flex-row gap-4 border-b border-[#DDD6C4] pb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-0 top-1/2 -translate-y-1/2 text-[#6E7A4E]" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search crop, diagnosis, plot…"
              className="w-full bg-transparent border-0 border-b border-[#C9C0A8] pl-7 py-2 text-sm focus:outline-none focus:border-[#1C2A1A]"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <FilterChip active={selectedCropFilter === 'all'} onClick={() => setSelectedCropFilter('all')}>All</FilterChip>
            {uniqueCrops.map((crop) => (
              <FilterChip key={crop} active={selectedCropFilter === crop} onClick={() => setSelectedCropFilter(crop)}>
                {crop}
              </FilterChip>
            ))}
          </div>
        </div>

        {filteredItems.length === 0 ? (
          <div className="py-20 text-center">
            <p className="font-display text-3xl text-[#161A12]">The archive is still empty</p>
            <p className="mt-3 text-[#5A6150] font-light">Run a detection to begin your field ledger.</p>
          </div>
        ) : (
          <div className="space-y-0 divide-y divide-[#DDD6C4]">
            {filteredItems.map((item) => (
              <article key={item.id} className="grid grid-cols-1 md:grid-cols-12 gap-6 py-8 items-center">
                <div className="md:col-span-3">
                  <img src={item.imageUrl} alt="" className="w-full h-40 object-cover" />
                </div>
                <div className="md:col-span-6 space-y-2">
                  <p className="text-[11px] tracking-[0.2em] uppercase text-[#6E7A4E]">{item.cropType}</p>
                  <h3 className="font-display text-2xl text-[#161A12]">{item.diagnosis.diseaseName}</h3>
                  <p className="text-sm text-[#5A6150] font-light line-clamp-2">{item.diagnosis.summary}</p>
                  <div className="flex flex-wrap gap-4 text-xs text-[#5A6150] pt-1">
                    <span className="inline-flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{new Date(item.timestamp).toLocaleDateString()}</span>
                    {item.location && <span className="inline-flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{item.location}</span>}
                  </div>
                </div>
                <div className="md:col-span-3 flex md:flex-col md:items-end gap-3">
                  <span className="text-xs uppercase tracking-widest text-[#6E7A4E]">{item.diagnosis.severity}</span>
                  <button
                    onClick={() => onSelectResult(item)}
                    className="px-5 py-2 rounded-full bg-[#1C2A1A] text-[#F6F1E6] text-sm"
                  >
                    Open reading
                  </button>
                  <button onClick={() => onDeleteItem(item.id)} className="text-xs text-[#8A3E38]">
                    Remove
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-1.5 rounded-full text-xs capitalize tracking-wide ${
        active ? 'bg-[#1C2A1A] text-[#F6F1E6]' : 'border border-[#C9C0A8] text-[#1C2A1A]'
      }`}
    >
      {children}
    </button>
  );
}
