import React, { useState } from 'react';
import { Search, Trash2, Calendar } from 'lucide-react';
import type { CropAnalysisSession } from '../types/session';
import { sessionDiagnosisTitle, formatOptionalPercent } from '../types/session';
import { PageBanner } from './PageBanner';
import { IMAGES } from '../data/images';

interface HistorySectionProps {
  historyItems: CropAnalysisSession[];
  onSelectResult: (result: CropAnalysisSession) => void;
  onClearHistory: () => void;
  onDeleteItem: (id: string) => void;
}

export const HistorySection: React.FC<HistorySectionProps> = ({
  historyItems = [],
  onSelectResult,
  onClearHistory,
  onDeleteItem,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = historyItems.filter((item) => {
    const title = sessionDiagnosisTitle(item).toLowerCase();
    return (
      title.includes(searchTerm.toLowerCase()) ||
      item.cropDeclaration.includes(searchTerm.toLowerCase()) ||
      (item.city && item.city.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  });

  return (
    <div className="bg-surface min-h-screen">
      <PageBanner
        kicker="History"
        title="A ledger of every field reading"
        subtitle="Live analyses stored in this browser session."
        image={IMAGES.wheat}
      />

      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 space-y-10">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
          <div>
            <p className="text-[11px] tracking-[0.28em] uppercase text-olive mb-2">Archive</p>
            <h2 className="font-display text-4xl text-ink">{historyItems.length} recorded scans</h2>
          </div>
          {historyItems.length > 0 && (
            <button onClick={onClearHistory} className="inline-flex items-center gap-2 text-sm text-[#8A3E38]">
              <Trash2 className="w-4 h-4" /> Clear archive
            </button>
          )}
        </div>

        <div className="relative max-w-md border-b border-border pb-6">
          <Search className="w-4 h-4 absolute left-0 top-1/2 -translate-y-1/2 text-olive" />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search diagnosis, declaration, city…"
            className="w-full bg-transparent pl-7 py-2 text-sm focus:outline-none"
          />
        </div>

        {filteredItems.length === 0 ? (
          <div className="py-20 text-center">
            <p className="font-display text-3xl text-ink">The archive is still empty</p>
            <p className="mt-3 text-ink-muted font-light">Run a detection against the live API to begin.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {filteredItems.map((item) => (
              <article key={item.id} className="border border-border p-6 space-y-3">
                <button type="button" onClick={() => onSelectResult(item)} className="text-left w-full">
                  <img src={item.imageUrl} alt="" className="w-full h-40 object-cover mb-4" />
                  <h3 className="font-display text-2xl text-ink">{sessionDiagnosisTitle(item)}</h3>
                  <p className="text-sm text-ink-muted flex items-center gap-2 mt-2">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                  <p className="text-xs text-olive mt-2">
                    Routing: {item.report.specialist_routing.routing_status} · Confidence:{' '}
                    {formatOptionalPercent(item.report.disease.confidence)}
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteItem(item.id)}
                  className="text-xs text-[#8A3E38]"
                >
                  Remove
                </button>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
