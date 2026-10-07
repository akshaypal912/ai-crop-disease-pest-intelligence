import type { PredictionResponse } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportRiskWeatherCard({ report }: { report: PredictionResponse }) {

  const { localize } = useFarmerLanguage();

  const { weather, risk } = report;

  const insufficient =

    risk.status === 'INSUFFICIENT_DATA' || risk.risk_level === 'INSUFFICIENT_DATA';



  const riskHeadline = insufficient

    ? localize('Risk: insufficient data')

    : `Risk: ${risk.risk_level || 'Unknown'}`;



  return (

    <article className="border-t border-border pt-8 space-y-6">

      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">

        {localize('Weather & risk')}

      </p>

      {weather?.weather_available ? (

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">

          <Metric

            label={localize('Location')}

            value={[weather.location_name, weather.country].filter(Boolean).join(', ') || '—'}

          />

          <Metric

            label={localize('Temp')}

            value={weather.temperature_c != null ? `${weather.temperature_c}°C` : '—'}

          />

          <Metric

            label={localize('Humidity')}

            value={weather.humidity_pct != null ? `${weather.humidity_pct}%` : '—'}

          />

          <Metric

            label={localize('Rain (1h)')}

            value={weather.rainfall_mm != null ? `${weather.rainfall_mm} mm` : '—'}

          />

        </div>

      ) : (

        <p className="text-ink-muted font-light">

          {localize('Weather data unavailable for this request.')}

        </p>

      )}

      <div>

        <h3 className="font-display text-2xl text-ink">{riskHeadline}</h3>

        {!insufficient && risk.risk_score != null && (

          <p className="text-sm text-ink-muted mt-1">

            {localize('Score:')} {risk.risk_score.toFixed(2)} / 1.00

          </p>

        )}

        {insufficient && (

          <p className="text-sm text-ink-muted mt-1">{localize('Risk score: Unavailable')}</p>

        )}

        {risk.factors?.length > 0 && (

          <ul className="mt-3 space-y-1 text-sm text-ink-muted font-light">

            {risk.factors.map((f) => (

              <li key={f}>{localize(f)}</li>

            ))}

          </ul>

        )}

        {risk.message && <p className="text-sm text-ink-muted mt-2">{localize(risk.message)}</p>}

      </div>

    </article>

  );

}



function Metric({ label, value }: { label: string; value: string }) {

  return (

    <div>

      <p className="text-[11px] uppercase tracking-widest text-olive">{label}</p>

      <p className="font-display text-lg mt-1">{value}</p>

    </div>

  );

}


