import React, { useState } from 'react';
import type { Recommendation } from '../types/crop';

export const RecommendationsCard: React.FC<{ recommendations: Recommendation[] }> = ({
  recommendations = [],
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'monitor' | 'field_care' | 'follow_up'>('all');
  const [completedIds, setCompletedIds] = useState<string[]>([]);

  const filtered =
    activeTab === 'all' ? recommendations : recommendations.filter((r) => r.category === activeTab);

  return (
    <article className="border-t border-[#DDD6C4] pt-8 space-y-6">
      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">Field guidance</p>
      <h3 className="font-display text-2xl text-[#161A12]">What to do next</h3>

      <div className="flex flex-wrap gap-2">
        {(['all', 'monitor', 'field_care', 'follow_up'] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-full text-xs capitalize ${
              activeTab === tab ? 'bg-[#1C2A1A] text-[#F6F1E6]' : 'border border-[#C9C0A8] text-[#1C2A1A]'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="space-y-6">
        {filtered.map((rec) => {
          const done = completedIds.includes(rec.id);
          return (
            <button
              key={rec.id}
              type="button"
              onClick={() =>
                setCompletedIds((prev) =>
                  prev.includes(rec.id) ? prev.filter((i) => i !== rec.id) : [...prev, rec.id]
                )
              }
              className={`block w-full text-left ${done ? 'opacity-50' : ''}`}
            >
              <p className="text-[11px] uppercase tracking-widest text-[#6E7A4E] mb-1">{rec.urgency} · {rec.category.replace('_', ' ')}</p>
              <h4 className={`font-display text-xl ${done ? 'line-through' : ''}`}>{rec.title}</h4>
              <p className="text-sm text-[#5A6150] font-light mt-1">{rec.description}</p>
            </button>
          );
        })}
      </div>
    </article>
  );
};
