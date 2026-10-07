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

    <article className="border-t border-border pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">

        {localize('Validated disease specialist')}

      </p>

      <h2 className="font-display text-4xl text-ink leading-tight">{title}</h2>

      {d.scientific_name && d.name && (

        <p className="italic text-ink-muted">{d.scientific_name}</p>

      )}

      <p className="text-sm text-ink-muted">

        {localize('Status:')} <strong>{d.prediction_status}</strong>

      </p>

      <p className="text-sm text-ink-muted">

        {localize('Confidence:')} <strong>{formatOptionalPercent(d.confidence)}</strong>

      </p>

      {sev.level && (

        <p className="text-sm text-ink-muted">

          {localize('Severity:')} {sev.level}

          {sev.visible_affected_area_percentage != null

            ? ` (~${sev.visible_affected_area_percentage.toFixed(1)}% affected)`

            : ''}

        </p>

      )}

      {d.status_message && (

        <p className="text-ink-muted font-light leading-relaxed">

          {localize(neutralizeVisionProviderCopy(d.status_message))}

        </p>

      )}

    </article>

  );

}


