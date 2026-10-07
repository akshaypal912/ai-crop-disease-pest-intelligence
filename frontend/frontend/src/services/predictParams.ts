import type { CropDeclarationChoice } from '../types/session';

export function declaredCropFromChoice(choice: CropDeclarationChoice): string | undefined {
  if (choice === 'tomato') return 'Tomato';
  if (choice === 'other') return 'Other';
  return undefined;
}

export function buildPredictQueryParams(options: {
  cropDeclaration: CropDeclarationChoice;
  city?: string;
  growthStage?: string;
}): Record<string, string> {
  const params: Record<string, string> = {};
  const city = options.city?.trim();
  if (city) params.city = city;
  if (options.growthStage) params.growth_stage = options.growthStage;
  const declared = declaredCropFromChoice(options.cropDeclaration);
  if (declared) params.declared_crop = declared;
  return params;
}

/** Map UI growth stage to backend-supported values. */
export function normalizeGrowthStage(stage: string): string | undefined {
  const map: Record<string, string> = {
    seedling: 'seedling',
    vegetative: 'vegetative',
    flowering: 'flowering',
    fruiting: 'fruiting',
    harvest: 'ripening',
    ripening: 'ripening',
  };
  return map[stage];
}
