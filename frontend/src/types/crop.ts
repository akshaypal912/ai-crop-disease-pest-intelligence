export type CropType = 'tomato' | 'potato' | 'corn' | 'apple' | 'wheat' | 'cotton' | 'rice' | 'other';

export type GrowthStage = 'seedling' | 'vegetative' | 'flowering' | 'fruiting' | 'harvest';

export type Severity = 'healthy' | 'mild' | 'moderate' | 'severe' | 'uncertain';

export type RiskLevel = 'low' | 'moderate' | 'high' | 'critical' | 'insufficient_data';

export interface BoundingBox {
  id: string;
  label: string;
  confidence: number;
  x: number; // percentage (0-100)
  y: number; // percentage (0-100)
  width: number; // percentage (0-100)
  height: number; // percentage (0-100)
  type: 'lesion' | 'pest' | 'symptom';
}

export interface DiseaseDiagnosis {
  diseaseName: string;
  scientificName?: string;
  confidence: number; // 0 - 100
  isReliable: boolean;
  severity: Severity;
  summary: string;
  boundingBoxes: BoundingBox[];
}

export interface PestDetection {
  detected: boolean;
  pestName?: string;
  pestCount?: number;
  confidence?: number;
  boundingBoxes: BoundingBox[];
  notes?: string;
}

export interface EnvironmentalContext {
  temperature?: number; // °C
  humidity?: number; // %
  rainfall?: number; // mm
  leafWetnessHours?: number; // hrs
  isDataSufficient: boolean;
  missingFields?: string[];
}

export interface RiskAssessment {
  riskLevel: RiskLevel;
  contributingFactors: string[];
  isDataSufficient: boolean;
  explanation: string;
}

export interface Recommendation {
  id: string;
  category: 'monitor' | 'field_care' | 'follow_up';
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high';
}

export interface Alert {
  id: string;
  severity: 'warning' | 'critical' | 'info';
  reason: string;
  timestamp: string;
  action: string;
  cropType?: string;
}

export interface AnalysisResult {
  id: string;
  timestamp: string;
  imageUrl: string;
  cropType: CropType;
  growthStage?: GrowthStage;
  location?: string;
  diagnosis: DiseaseDiagnosis;
  pests: PestDetection;
  environment: EnvironmentalContext;
  risk: RiskAssessment;
  recommendations: Recommendation[];
  alerts: Alert[];
}

export interface SampleCropImage {
  id: string;
  name: string;
  cropType: CropType;
  description: string;
  imageUrl: string;
  mockResult: AnalysisResult;
}
