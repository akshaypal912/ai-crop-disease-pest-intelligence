import React, { useEffect } from 'react';

import { ArrowLeft, Printer } from 'lucide-react';

import type { CropAnalysisSession } from '../types/session';

import { sessionDiagnosisTitle } from '../types/session';

import { DetectionOverlay } from './DetectionOverlay';

import { VisionAssessmentCard } from './VisionAssessmentCard';

import { SpecialistRoutingCard } from './SpecialistRoutingCard';

import { ReportDiagnosisCard } from './ReportDiagnosisCard';

import { ReportPestCard } from './ReportPestCard';

import { ReportRiskWeatherCard } from './ReportRiskWeatherCard';

import { ReportRecommendationsCard } from './ReportRecommendationsCard';

import { ReportAlertBanner } from './ReportAlertBanner';

import { pestsToOverlayBoxes } from '../utils/pestOverlay';

import { IMAGES } from '../data/images';

import { CropAssistant } from './CropAssistant';

import { useFarmerLanguage } from '../i18n/FarmerLanguageContext';

import {

  collectReportTranslatableStrings,

  RESULT_PAGE_UI_STRINGS,

} from '../utils/collectReportText';



interface ResultsViewProps {

  session: CropAnalysisSession;

  onBack: () => void;

  onAnalyzeAnother: () => void;

}



export const ResultsView: React.FC<ResultsViewProps> = ({

  session,

  onBack,

  onAnalyzeAnother,

}) => {

  const { report } = session;

  const pestBoxes = pestsToOverlayBoxes(report.pests);

  const { localize, ingestTranslations, translationWarning } = useFarmerLanguage();



  useEffect(() => {

    const strings = [

      ...collectReportTranslatableStrings(report),

      ...RESULT_PAGE_UI_STRINGS,

    ];

    void ingestTranslations(strings);

  }, [report, ingestTranslations]);



  return (

    <div className="bg-[#FBF7EE] min-h-screen">

      {translationWarning && (

        <p

          role="status"

          className="text-center text-xs text-[#7A5A20] bg-[#FFF3DC] border-b border-[#E8C882] py-2 px-4"

        >

          {localize(translationWarning)}

        </p>

      )}

      <section className="relative overflow-hidden min-h-[38vh]">

        <img src={IMAGES.sunsetFarm} alt="" className="absolute inset-0 w-full h-full object-cover" />

        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(18,25,16,0.78)_0%,rgba(18,25,16,0.4)_100%)]" />

        <div className="relative z-10 max-w-[1400px] mx-auto px-6 sm:px-10 pt-28 pb-12">

          <button onClick={onBack} className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[#E8D5A3] mb-6">

            <ArrowLeft className="w-4 h-4" /> {localize('Return to detect')}

          </button>

          <p className="text-[11px] tracking-[0.28em] uppercase text-[#E8D5A3] mb-3">Result · {session.id}</p>

          <h1 className="font-display text-[#F4E7C0] text-[42px] sm:text-[62px] leading-[0.98] max-w-4xl">

            {sessionDiagnosisTitle(session)}

          </h1>

          <p className="mt-4 text-white/75 max-w-xl font-light">

            Declaration: {session.cropDeclaration} · {session.city || 'No city'} ·{' '}

            {new Date(session.timestamp).toLocaleString()}

          </p>

          <div className="mt-8 flex flex-wrap gap-3">

            <button

              onClick={onAnalyzeAnother}

              className="px-6 py-2.5 rounded-full bg-[#E8D5A3] text-[#1C2A1A] text-sm font-semibold"

            >

              {localize('Detect another crop')}

            </button>

            <button

              onClick={() => window.print()}

              className="px-6 py-2.5 rounded-full border border-white/30 text-white text-sm inline-flex items-center gap-2"

            >

              <Printer className="w-4 h-4" /> {localize('Print reading')}

            </button>

          </div>

        </div>

      </section>



      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 py-16 grid grid-cols-1 lg:grid-cols-12 gap-12">

        <div className="lg:col-span-5 space-y-6">

          <DetectionOverlay imageUrl={session.imageUrl} boundingBoxes={[]} pestBoxes={pestBoxes} />

          <ReportAlertBanner alert={report.alert} />

        </div>

        <div className="lg:col-span-7 space-y-6">

          <VisionAssessmentCard vision={report.vision_assessment} />

          <SpecialistRoutingCard routing={report.specialist_routing} />

          <ReportDiagnosisCard report={report} />

          <ReportPestCard pests={report.pests} pestRecommendations={report.pest_recommendations} />

          <ReportRiskWeatherCard report={report} />

          <ReportRecommendationsCard recommendations={report.recommendations} />

        </div>

      </div>



      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 pb-20">

        <CropAssistant report={report} sessionId={session.id} />

      </div>

    </div>

  );

};


