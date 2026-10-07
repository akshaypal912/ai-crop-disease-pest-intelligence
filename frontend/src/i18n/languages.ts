export type FarmerLanguageCode =
  | 'en'
  | 'hi'
  | 'bn'
  | 'mr'
  | 'gu'
  | 'pa'
  | 'ta'
  | 'te'
  | 'kn'
  | 'ml'
  | 'ur';

export interface FarmerLanguageOption {
  code: FarmerLanguageCode;
  label: string;
  nativeLabel: string;
}

export const FARMER_LANGUAGES: FarmerLanguageOption[] = [
  { code: 'en', label: 'English', nativeLabel: 'English' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी' },
  { code: 'gu', label: 'Gujarati', nativeLabel: 'ગુજરાતી' },
  { code: 'pa', label: 'Punjabi', nativeLabel: 'ਪੰਜਾਬੀ' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'Malayalam', nativeLabel: 'മലയാളം' },
  { code: 'ur', label: 'Urdu', nativeLabel: 'اردو' },
];

export const DEFAULT_LANGUAGE: FarmerLanguageCode = 'en';
export const LANGUAGE_STORAGE_KEY = 'cropsense_farmer_language_v1';

export const TRANSLATION_UNAVAILABLE_MSG =
  'Translation is temporarily unavailable. Showing English.';
