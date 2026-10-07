export type DiseaseCategory = 'Disease' | 'Pest';

export type DiseaseSeverityLevel = 'Low' | 'Moderate' | 'High';

export interface DiseaseFavorableConditions {
  temperature: string;
  humidity: string;
  moisture: string;
  other: string[];
}

export interface DiseaseLibraryEntry {
  id: string;
  name: string;
  crop: string;
  category: DiseaseCategory;
  image: string;
  sampleId: string;
  shortDescription: string;
  overview: string;
  symptoms: string[];
  causes: string[];
  favorableConditions: DiseaseFavorableConditions;
  severity: DiseaseSeverityLevel;
  severityExplanation: string;
  prevention: string[];
  management: string[];
  whenToAct: string;
  detectionNotes: string;
  metaDescription: string;
}
