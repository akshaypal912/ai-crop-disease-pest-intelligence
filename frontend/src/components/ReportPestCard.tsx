import type { PestDetectionItem, PestRecommendationBundle } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportPestCard({

  pests,

  pestRecommendations,

}: {

  pests: PestDetectionItem[];

  pestRecommendations: PestRecommendationBundle[];

}) {

  const { localize } = useFarmerLanguage();



  return (

    <article className="border-t border-[#DDD6C4] pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">

        {localize('Pest detection (Pest24 YOLO)')}

      </p>

      {pests.length === 0 ? (

        <p className="font-display text-xl text-[#161A12]">

          {localize('No supported pest instances detected in this image.')}

        </p>

      ) : (

        <ul className="space-y-3">

          {pests.map((p, i) => (

            <li key={`${p.pest}-${i}`} className="text-sm text-[#5A6150]">

              <strong className="text-[#161A12]">{p.pest}</strong> — {localize('detection confidence')}{' '}

              {(p.confidence * 100).toFixed(1)}% · box [{p.bounding_box.join(', ')}]

            </li>

          ))}

        </ul>

      )}

      {pestRecommendations.length > 0 && (

        <div className="space-y-2 pt-2">

          <p className="text-sm font-medium text-[#161A12]">{localize('IPM guidance bundles')}</p>

          {pestRecommendations.map((b) => (

            <p key={b.pest} className="text-sm text-[#5A6150] font-light">

              {b.pest} · {localize(b.recommendation_status)} · tier {localize(b.detection_confidence_label)}

            </p>

          ))}

        </div>

      )}

    </article>

  );

}


