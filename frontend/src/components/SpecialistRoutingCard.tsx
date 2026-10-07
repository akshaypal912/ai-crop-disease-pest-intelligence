import type { SpecialistRouting } from '../types/predict';

import { neutralizeVisionProviderCopy } from '../utils/visionCopy';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function SpecialistRoutingCard({ routing }: { routing: SpecialistRouting }) {

  const { localize } = useFarmerLanguage();

  let headline = 'No validated disease specialist';

  let detail = neutralizeVisionProviderCopy(routing.reason);



  if (routing.routing_status === 'TOMATO_SPECIALIST') {

    headline = 'Tomato validated specialist active';

    detail = neutralizeVisionProviderCopy(routing.reason);

  } else if (routing.routing_status === 'CONFIRMATION_REQUIRED') {

    headline = 'Tomato confirmation required';

    detail = neutralizeVisionProviderCopy(routing.reason);

  }



  return (

    <article className="border-t border-border pt-8 space-y-3">

      <p className="text-[11px] tracking-[0.28em] uppercase text-olive">

        {localize('Specialist routing')}

      </p>

      <h3 className="font-display text-2xl text-ink">{localize(headline)}</h3>

      <p className="text-sm text-ink-muted font-light">{localize(detail)}</p>

      <p className="text-xs uppercase tracking-widest text-olive">

        {localize('Status:')} {routing.routing_status} · {localize('Source:')} {routing.crop_source}

      </p>

    </article>

  );

}


