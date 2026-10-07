import { TRANSLATION_UNAVAILABLE_MSG } from '../i18n/languages';
import { puterTranslateTexts } from './puterTranslate';

export interface BatchTranslateResponse {
  items: { translated_text: string; translation_available: boolean }[];
  target_language: string;
  translation_available: boolean;
  warning?: string | null;
}

const memoryCache = new Map<string, string>();

function cacheKey(lang: string, text: string): string {
  return `${lang}::${text}`;
}

/**
 * Batch translate farmer-facing strings (Puter.js client-side).
 * Preserves the same response shape previously returned by POST /translate/batch.
 */
export async function translateBatch(
  texts: string[],
  targetLanguage: string
): Promise<BatchTranslateResponse> {
  if (targetLanguage === 'en') {
    return {
      items: texts.map((t) => ({ translated_text: t, translation_available: true })),
      target_language: 'en',
      translation_available: true,
    };
  }

  const unique: string[] = [];
  const seen = new Set<string>();
  for (const t of texts) {
    if (!t?.trim() || seen.has(t)) continue;
    seen.add(t);
    unique.push(t);
  }

  const cachedResults = new Map<string, string>();
  const toFetch: string[] = [];
  for (const t of unique) {
    const key = cacheKey(targetLanguage, t);
    const hit = memoryCache.get(key);
    if (hit !== undefined) {
      cachedResults.set(t, hit);
    } else {
      toFetch.push(t);
    }
  }

  let batchAvailable = true;
  if (toFetch.length > 0) {
    const { translations, available } = await puterTranslateTexts(toFetch, targetLanguage);
    batchAvailable = available;
    toFetch.forEach((src, i) => {
      const translated = translations[i] ?? src;
      memoryCache.set(cacheKey(targetLanguage, src), translated);
      cachedResults.set(src, translated);
    });
  }

  return {
    items: texts.map((t) => ({
      translated_text: cachedResults.get(t) ?? t,
      translation_available: batchAvailable,
    })),
    target_language: targetLanguage,
    translation_available: batchAvailable,
    warning: batchAvailable ? null : TRANSLATION_UNAVAILABLE_MSG,
  };
}
