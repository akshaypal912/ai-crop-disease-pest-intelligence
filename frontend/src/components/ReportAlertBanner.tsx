import type { AlertResult } from '../types/predict';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';



export function ReportAlertBanner({ alert }: { alert: AlertResult }) {

  const { localize } = useFarmerLanguage();



  if (!alert.active) {

    return (

      <p className="text-sm text-[#5A6150] font-light border border-[#DDD6C4] p-4">

        {localize('No active high-risk alert for this analysis.')}

      </p>

    );

  }

  return (

    <div className="border border-[#8A3E38] bg-[#F6F1E6] p-4 space-y-2">

      <p className="font-display text-xl text-[#8A3E38]">

        {localize(alert.title || 'Crop health alert')}

      </p>

      <ul className="list-disc pl-5 text-sm text-[#5A6150]">

        {alert.reasons.map((r) => (

          <li key={r}>{localize(r)}</li>

        ))}

      </ul>

    </div>

  );

}


