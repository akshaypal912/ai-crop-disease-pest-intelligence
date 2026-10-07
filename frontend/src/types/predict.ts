/** FastAPI /predict and /health response shapes (matches api/main.py). */

export interface HealthResponse {
  status: string;
  crop: string;
  model_loaded: boolean;
  version: string;
  weather_configured: boolean;
  pest_model_available: boolean;
  vision_llm_enabled: boolean;
  vision_llm_configured: boolean;
  vision_llm_model: string;
}

export interface VisionAssessment {
  likely_crop: string | null;
  crop_confidence: string | null;
  visible_symptoms: string[];
  possible_diseases: string[];
  possible_pests: string[];
  uncertainty_notes: string[];
  image_quality_notes: string[];
  assessment_type: string;
  provider?: string | null;
  model?: string | null;
}

export interface SpecialistRouting {
  routing_status: 'NO_SPECIALIST' | 'TOMATO_SPECIALIST' | 'CONFIRMATION_REQUIRED';
  selected_specialist: string | null;
  crop_source: 'USER_DECLARATION' | 'VISION_ASSESSMENT' | 'NONE';
  confirmation_required: boolean;
  reason: string;
}

export interface DiseaseResult {
  name: string | null;
  confidence: number | null;
  prediction_status: string;
  status_message: string | null;
  class_probabilities?: Record<string, number>;
  scientific_name?: string | null;
  symptoms?: string[];
  general_causes?: string[];
  favorable_conditions?: string[];
  general_preventive_information?: string[];
  disclaimer?: string | null;
}

export interface SeverityResult {
  status: string;
  level: string | null;
  visible_affected_area_percentage: number | null;
  method?: string | null;
  message?: string | null;
}

export interface PestDetectionItem {
  pest: string;
  confidence: number;
  bounding_box: number[];
}

export interface WeatherResult {
  weather_available: boolean;
  location_name?: string | null;
  country?: string | null;
  temperature_c?: number | null;
  humidity_pct?: number | null;
  rainfall_mm?: number | null;
  wind_speed_ms?: number | null;
  condition?: string | null;
  description?: string | null;
  observed_at_utc?: string | null;
  error?: string | null;
}

export interface RiskResult {
  status: string;
  risk_level: string | null;
  risk_score: number | null;
  factors: string[];
  sub_scores?: Record<string, number>;
  disclaimer?: string | null;
  message?: string | null;
}

export interface RecommendationItem {
  category: string;
  message: string;
  source?: string | null;
}

export interface PestRecommendationBundle {
  pest: string;
  confidence: number;
  bounding_box: number[];
  detection_confidence_label: string;
  recommendation_status: string;
  model_detection_note: string;
  recommendations: Record<string, string[]>;
}

export interface AlertResult {
  active: boolean;
  severity?: string | null;
  title?: string | null;
  reasons: string[];
  suppressed?: boolean;
  suppression_reason?: string | null;
}

export interface PredictionResponse {
  crop: string | null;
  disease: DiseaseResult;
  severity: SeverityResult;
  pests: PestDetectionItem[];
  weather: WeatherResult | null;
  risk: RiskResult;
  recommendations: RecommendationItem[];
  pest_recommendations: PestRecommendationBundle[];
  vision_assessment: VisionAssessment | null;
  specialist_routing: SpecialistRouting;
  alert: AlertResult;
  vision_error_category?: string | null;
  vision_error_type?: string | null;
  vision_error_message?: string | null;
}
