import React from 'react';
import type { PestDetection } from '../types/crop';

export const PestDetectionCard: React.FC<{ pests: PestDetection }> = ({ pests }) => {
  return (
    <article className="border-t border-[#DDD6C4] pt-8 space-y-3">
      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">Pests & vectors</p>
      {!pests.detected ? (
        <p className="font-display text-2xl text-[#161A12]">No active insect pressure visible on this sample.</p>
      ) : (
        <>
          <h3 className="font-display text-2xl text-[#161A12]">{pests.pestName || 'Insect activity identified'}</h3>
          {pests.pestCount != null && (
            <p className="text-sm text-[#5A6150]">Estimated density: {pests.pestCount} per leaf</p>
          )}
          {pests.notes && <p className="text-[#5A6150] font-light">{pests.notes}</p>}
        </>
      )}
    </article>
  );
};
