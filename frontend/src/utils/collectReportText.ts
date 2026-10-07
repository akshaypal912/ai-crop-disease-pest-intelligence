import type { PredictionResponse } from '../types/predict';

/** Collect unique farmer-facing strings from a /predict report (canonical English). */
export function collectReportTranslatableStrings(report: PredictionResponse): string[] {
  const set = new Set<string>();

  const add = (value: string | null | undefined) => {
    if (value && value.trim()) set.add(value.trim());
  };

  const va = report.vision_assessment;
  if (va) {
    add(va.likely_crop ?? undefined);
    add(va.crop_confidence ?? undefined);
    va.visible_symptoms?.forEach(add);
    va.possible_diseases?.forEach(add);
    va.possible_pests?.forEach(add);
    va.uncertainty_notes?.forEach(add);
    va.image_quality_notes?.forEach(add);
  }

  add(report.specialist_routing?.reason);
  add(report.disease?.name ?? undefined);
  add(report.disease?.status_message ?? undefined);
  add(report.disease?.scientific_name ?? undefined);
  report.disease?.symptoms?.forEach(add);
  report.disease?.general_causes?.forEach(add);
  report.disease?.favorable_conditions?.forEach(add);
  report.disease?.general_preventive_information?.forEach(add);
  add(report.disease?.disclaimer ?? undefined);

  report.pests?.forEach((p) => add(p.pest));
  report.pest_recommendations?.forEach((b) => {
    add(b.pest);
    add(b.detection_confidence_label);
    add(b.recommendation_status);
    add(b.model_detection_note);
    const rec = b.recommendations;
    if (rec && typeof rec === 'object') {
      Object.values(rec).forEach((section) => {
        if (Array.isArray(section)) section.forEach(add);
      });
    }
  });

  const w = report.weather;
  if (w) {
    add(w.location_name ?? undefined);
    add(w.description ?? undefined);
    add(w.condition ?? undefined);
    add(w.error ?? undefined);
  }

  const risk = report.risk;
  if (risk) {
    add(risk.message ?? undefined);
    add(risk.disclaimer ?? undefined);
    risk.factors?.forEach(add);
  }

  report.recommendations?.forEach((r) => {
    add(r.category);
    add(r.message);
  });

  const alert = report.alert;
  if (alert) {
    add(alert.title ?? undefined);
    add(alert.suppression_reason ?? undefined);
    alert.reasons?.forEach(add);
  }

  return [...set];
}

export const RESULT_PAGE_UI_STRINGS = [
  'Return to detect',
  'Detect another crop',
  'Print reading',
  'AI visual assessment',
  'Not a validated specialist diagnosis. Possible diseases and pests below are visual suggestions only.',
  'AI visual assessment unavailable.',
  'Likely crop:',
  'Not identified',
  'Crop confidence (qualitative):',
  'Unavailable',
  'Visible symptoms',
  'Possible diseases (not confirmed)',
  'Possible pests (not YOLO detections)',
  'Uncertainty notes',
  'Image quality notes',
  'None noted.',
  'Specialist routing',
  'No validated disease specialist',
  'Tomato validated specialist active',
  'Tomato confirmation required',
  'Validated disease specialist',
  'Specialist withheld',
  'Diagnosis unavailable',
  'Status:',
  'Source:',
  'Confidence:',
  'Severity:',
  'Pest detection (Pest24 YOLO)',
  'No supported pest instances detected in this image.',
  'detection confidence',
  'IPM guidance bundles',
  'Weather & risk',
  'Location',
  'Temp',
  'Humidity',
  'Rain (1h)',
  'Weather data unavailable for this request.',
  'Risk: insufficient data',
  'Score:',
  'Risk score: Unavailable',
  'Recommendations',
  'No specific recommendations from the backend for this analysis.',
  'Source:',
  'No active high-risk alert for this analysis.',
  'Crop health alert',
  'Translation is temporarily unavailable. Showing English.',
];

export const APP_SHELL_UI_STRINGS = [
  'Home',
  'Detect',
  'History',
  'Dashboard',
  'Detect Disease',
  'Backend connected',
  'Backend unavailable',
];

export const CROP_ASSISTANT_UI_STRINGS = [
  'AI Crop Assistant',
  'Ask questions about this crop analysis',
  'Suggested',
  'What should I do today?',
  'Why was this result given?',
  'What symptoms should I monitor?',
  'Are the detected pests concerning?',
  'What should I check tomorrow?',
  'Ask about this crop analysis…',
  'Ask',
  'AI Crop Assistant · Analysing…',
  'AI Crop Assistant is temporarily unavailable.',
  'Your crop analysis is still available above.',
  'Limited context',
  'Context used:',
  'Crop ID',
  'Pest detection',
  'Pest recommendations',
  'Weather',
  'Risk assessment',
  'Alert',
  'Disease diagnosis',
];

export const UPLOAD_UI_STRINGS = [
  'Detect',
  'Bring the field to the lens',
  'Upload a leaf or canopy photograph. Results come from the live FastAPI pipeline — no mock diagnoses.',
  'Backend unavailable. Start FastAPI with',
  'before analyzing.',
  'Drop a crop image',
  'JPEG, PNG or WEBP.',
  'Browse',
  'Analysis settings',
  'Crop declaration',
  'Crop declaration enables a validated crop-specific specialist. AI visual assessment does not automatically activate a specialist.',
  'Auto / Not specified',
  'Tomato',
  'Other / Non-Tomato',
  'Growth stage',
  'Seedling',
  'Vegetative',
  'Flowering',
  'Fruiting',
  'Ripening / harvest',
  'City (optional)',
  'e.g. Mumbai',
  'Analyzing crop…',
  'Analyze crop health',
];
