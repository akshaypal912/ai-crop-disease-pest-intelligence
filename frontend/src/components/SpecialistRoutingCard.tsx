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

    <article className="border-t border-[#DDD6C4] pt-8 space-y-3">

      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">

        {localize('Specialist routing')}

      </p>

      <h3 className="font-display text-2xl text-[#161A12]">{localize(headline)}</h3>

      <p className="text-sm text-[#5A6150] font-light">{localize(detail)}</p>

      <p className="text-xs uppercase tracking-widest text-[#6E7A4E]">

        {localize('Status:')} {routing.routing_status} · {localize('Source:')} {routing.crop_source}

      </p>

    </article>

  );

}


