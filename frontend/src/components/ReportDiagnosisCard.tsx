import type { PredictionResponse } from '../types/predict';

import { formatOptionalPercent } from '../types/session';

import { neutralizeVisionProviderCopy } from '../utils/visionCopy';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportDiagnosisCard({ report }: { report: PredictionResponse }) {

  const { localize } = useFarmerLanguage();

  const d = report.disease;

  const sev = report.severity;



  const title =

    d.name ||

    (report.specialist_routing.routing_status === 'CONFIRMATION_REQUIRED'

      ? 'Specialist withheld'

      : 'Diagnosis unavailable');



  return (

    <article className="border-t border-[#DDD6C4] pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">

        {localize('Validated disease specialist')}

      </p>

      <h2 className="font-display text-4xl text-[#161A12] leading-tight">{title}</h2>

      {d.scientific_name && d.name && (

        <p className="italic text-[#5A6150]">{d.scientific_name}</p>

      )}

      <p className="text-sm text-[#5A6150]">

        {localize('Status:')} <strong>{d.prediction_status}</strong>

      </p>

      <p className="text-sm text-[#5A6150]">

        {localize('Confidence:')} <strong>{formatOptionalPercent(d.confidence)}</strong>

      </p>

      {sev.level && (

        <p className="text-sm text-[#5A6150]">

          {localize('Severity:')} {sev.level}

          {sev.visible_affected_area_percentage != null

            ? ` (~${sev.visible_affected_area_percentage.toFixed(1)}% affected)`

            : ''}

        </p>

      )}

      {d.status_message && (

        <p className="text-[#5A6150] font-light leading-relaxed">

          {localize(neutralizeVisionProviderCopy(d.status_message))}

        </p>

      )}

    </article>

  );

}


