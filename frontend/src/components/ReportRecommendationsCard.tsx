import type { RecommendationItem } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportRecommendationsCard({ recommendations }: { recommendations: RecommendationItem[] }) {

  const { localize } = useFarmerLanguage();



  return (

    <article className="border-t border-border pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">

        {localize('Recommendations')}

      </p>

      {!recommendations.length ? (

        <p className="text-ink-muted font-light">

          {localize('No specific recommendations from the backend for this analysis.')}

        </p>

      ) : (

        <ul className="space-y-4">

          {recommendations.map((r, i) => (

            <li key={`${r.category}-${i}`}>

              <p className="text-[11px] uppercase tracking-widest text-olive">{localize(r.category)}</p>

              <p className="text-sm text-ink-muted font-light mt-1">{localize(r.message)}</p>

              {r.source && (

                <p className="text-xs text-olive mt-1">

                  {localize('Source:')} {r.source}

                </p>

              )}

            </li>

          ))}

        </ul>

      )}

    </article>

  );

}


