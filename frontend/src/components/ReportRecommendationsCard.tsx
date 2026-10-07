import type { RecommendationItem } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportRecommendationsCard({ recommendations }: { recommendations: RecommendationItem[] }) {

  const { localize } = useFarmerLanguage();



  return (

    <article className="border-t border-[#DDD6C4] pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">

        {localize('Recommendations')}

      </p>

      {!recommendations.length ? (

        <p className="text-[#5A6150] font-light">

          {localize('No specific recommendations from the backend for this analysis.')}

        </p>

      ) : (

        <ul className="space-y-4">

          {recommendations.map((r, i) => (

            <li key={`${r.category}-${i}`}>

              <p className="text-[11px] uppercase tracking-widest text-[#6E7A4E]">{localize(r.category)}</p>

              <p className="text-sm text-[#5A6150] font-light mt-1">{localize(r.message)}</p>

              {r.source && (

                <p className="text-xs text-[#6E7A4E] mt-1">

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


