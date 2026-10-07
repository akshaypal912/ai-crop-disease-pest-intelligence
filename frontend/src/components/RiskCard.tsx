import React from 'react';
import type { EnvironmentalContext, RiskAssessment } from '../types/crop';

export const RiskCard: React.FC<{
  environment: EnvironmentalContext;
  risk: RiskAssessment;
}> = ({ environment, risk }) => {
  const isDataSufficient = environment.isDataSufficient && risk.isDataSufficient;

  return (
    <article className="border-t border-border pt-8 space-y-6">
      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">Microclimate & risk</p>
      <h3 className="font-display text-2xl text-ink">
        {isDataSufficient ? `${risk.riskLevel} field risk` : 'Weather data incomplete'}
      </h3>

      {!isDataSufficient ? (
        <p className="text-ink-muted font-light">{risk.explanation}</p>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <Metric label="Temp" value={environment.temperature != null ? `${environment.temperature}°C` : '—'} />
            <Metric label="Humidity" value={environment.humidity != null ? `${environment.humidity}%` : '—'} />
            <Metric label="Rain" value={environment.rainfall != null ? `${environment.rainfall} mm` : '—'} />
            <Metric label="Leaf wetness" value={environment.leafWetnessHours != null ? `${environment.leafWetnessHours} h` : '—'} />
          </div>
          <ul className="space-y-2 text-sm text-ink-muted font-light">
            {risk.contributingFactors.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
          {risk.explanation && <p className="text-sm text-ink-muted font-light">{risk.explanation}</p>}
        </>
      )}
    </article>
  );
};

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-widest text-olive">{label}</p>
      <p className="font-display text-2xl mt-1">{value}</p>
    </div>
  );
}
