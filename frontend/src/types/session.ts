import type { PredictionResponse } from './predict';

export type CropDeclarationChoice = 'auto' | 'tomato' | 'other';

export const CROP_DECLARATION_LABELS: Record<CropDeclarationChoice, string> = {
  auto: 'Auto / Not specified',
  tomato: 'Tomato',
  other: 'Other / Non-Tomato',
};

export interface CropAnalysisSession {
  id: string;
  timestamp: string;
  imageUrl: string;
  cropDeclaration: CropDeclarationChoice;
  city?: string;
  growthStage?: string;
  report: PredictionResponse;
}

export function sessionDiagnosisTitle(session: CropAnalysisSession): string {
  const d = session.report.disease;
  if (d.name) return d.name;
  if (d.prediction_status === 'UNSUPPORTED_CROP') {
    return session.report.specialist_routing.routing_status === 'CONFIRMATION_REQUIRED'
      ? 'Tomato confirmation required'
      : 'Disease diagnosis withheld';
  }
  return d.prediction_status.replace(/_/g, ' ');
}

export function formatOptionalPercent(value: number | null | undefined): string {
  if (value == null) return 'Unavailable';
  return `${(value * 100).toFixed(1)}%`;
}
