import type { VisionAssessment } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function VisionAssessmentCard({ vision }: { vision: VisionAssessment | null }) {

  const { localize } = useFarmerLanguage();



  return (

    <article className="border-t border-[#DDD6C4] pt-8 space-y-4">

      <p className="text-[11px] tracking-[0.28em] uppercase text-[#6E7A4E]">

        {localize('AI visual assessment')}

      </p>

      <p className="text-sm text-[#5A6150] font-light">

        {localize(

          'Not a validated specialist diagnosis. Possible diseases and pests below are visual suggestions only.'

        )}

      </p>

      {!vision ? (

        <p className="font-display text-xl text-[#161A12]">

          {localize('AI visual assessment unavailable.')}

        </p>

      ) : (

        <>

          <p>

            <span className="text-[#5A6150]">{localize('Likely crop:')} </span>

            <strong>{localize(vision.likely_crop || 'Not identified')}</strong>

          </p>

          <p>

            <span className="text-[#5A6150]">{localize('Crop confidence (qualitative):')} </span>

            {localize(vision.crop_confidence || 'Unavailable')}

          </p>

          <ListBlock title={localize('Visible symptoms')} items={vision.visible_symptoms} localize={localize} />

          <ListBlock

            title={localize('Possible diseases (not confirmed)')}

            items={vision.possible_diseases}

            localize={localize}

          />

          <ListBlock

            title={localize('Possible pests (not YOLO detections)')}

            items={vision.possible_pests}

            localize={localize}

          />

          <ListBlock title={localize('Uncertainty notes')} items={vision.uncertainty_notes} localize={localize} />

          <ListBlock title={localize('Image quality notes')} items={vision.image_quality_notes} localize={localize} />

          <p className="text-xs text-[#6E7A4E]">

            {vision.assessment_type}

            {vision.provider ? ` · ${vision.provider}` : ''}

            {vision.model ? ` · ${vision.model}` : ''}

          </p>

        </>

      )}

    </article>

  );

}



function ListBlock({

  title,

  items,

  localize,

}: {

  title: string;

  items: string[];

  localize: (t: string) => string;

}) {

  return (

    <div>

      <p className="text-sm font-medium text-[#161A12] mb-1">{title}</p>

      {items?.length ? (

        <ul className="list-disc pl-5 text-sm text-[#5A6150] font-light space-y-1">

          {items.map((line) => (

            <li key={line}>{localize(line)}</li>

          ))}

        </ul>

      ) : (

        <p className="text-sm text-[#5A6150] font-light">{localize('None noted.')}</p>

      )}

    </div>

  );

}


