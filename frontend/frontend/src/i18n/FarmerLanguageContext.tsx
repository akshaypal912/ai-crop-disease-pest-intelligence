import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  useEffect,
  type ReactNode,
} from 'react';
import {
  DEFAULT_LANGUAGE,
  FARMER_LANGUAGES,
  LANGUAGE_STORAGE_KEY,
  type FarmerLanguageCode,
} from './languages';
import { translateBatch } from '../services/translationApi';

interface FarmerLanguageContextValue {
  language: FarmerLanguageCode;
  setLanguage: (code: FarmerLanguageCode) => void;
  languages: typeof FARMER_LANGUAGES;
  localize: (text: string | null | undefined) => string;
  ingestTranslations: (strings: string[]) => Promise<void>;
  translationWarning: string | null;
  isTranslating: boolean;
}

const FarmerLanguageContext = createContext<FarmerLanguageContextValue | null>(null);

function readStoredLanguage(): FarmerLanguageCode {
  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored && FARMER_LANGUAGES.some((l) => l.code === stored)) {
      return stored as FarmerLanguageCode;
    }
  } catch {
    /* ignore */
  }
  return DEFAULT_LANGUAGE;
}

export function FarmerLanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<FarmerLanguageCode>(readStoredLanguage);
  const [map, setMap] = useState<Record<string, string>>({});
  const [translationWarning, setTranslationWarning] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    setMap({});
    setTranslationWarning(null);
  }, [language]);

  const setLanguage = useCallback((code: FarmerLanguageCode) => {
    setLanguageState(code);
    try {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, code);
    } catch {
      /* ignore */
    }
  }, []);

  const localize = useCallback(
    (text: string | null | undefined) => {
      if (!text) return '';
      if (language === 'en') return text;
      return map[text] ?? text;
    },
    [language, map]
  );

  const ingestTranslations = useCallback(
    async (strings: string[]) => {
      if (language === 'en') {
        setMap({});
        setTranslationWarning(null);
        return;
      }
      const unique = [...new Set(strings.filter((s) => s?.trim()))];
      if (unique.length === 0) return;

      setIsTranslating(true);
      try {
        const res = await translateBatch(unique, language);
        const next: Record<string, string> = {};
        unique.forEach((src, i) => {
          next[src] = res.items[i]?.translated_text ?? src;
        });
        setMap((prev) => ({ ...prev, ...next }));
        setTranslationWarning(res.warning ?? null);
      } finally {
        setIsTranslating(false);
      }
    },
    [language]
  );

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      languages: FARMER_LANGUAGES,
      localize,
      ingestTranslations,
      translationWarning,
      isTranslating,
    }),
    [language, setLanguage, localize, ingestTranslations, translationWarning, isTranslating]
  );

  return (
    <FarmerLanguageContext.Provider value={value}>{children}</FarmerLanguageContext.Provider>
  );
}

export function useFarmerLanguage(): FarmerLanguageContextValue {
  const ctx = useContext(FarmerLanguageContext);
  if (!ctx) {
    throw new Error('useFarmerLanguage must be used within FarmerLanguageProvider');
  }
  return ctx;
}
